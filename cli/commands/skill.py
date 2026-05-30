"""zv skill - Skill management commands."""

import os
import re
import sys
import json
import hashlib
import shutil
import zipfile
import tempfile
from dataclasses import dataclass, field
from typing import Optional, List

from urllib.parse import urlparse

import click
import requests

from cli.utils import (
    get_project_root,
    get_skills_dir,
    get_builtin_skills_dir,
    load_skills_config,
    SKILL_HUB_API,
    ensure_sys_path,
)


# ======================================================================
# Public types for the core install API (used by CLI and chat plugin)
# ======================================================================

class SkillInstallError(Exception):
    """Raised when skill installation fails."""
    pass


@dataclass
class InstallResult:
    """Result of a skill installation operation."""
    installed: List[str] = field(default_factory=list)
    messages: List[str] = field(default_factory=list)
    error: Optional[str] = None


@dataclass
class SkillSummaryTarget:
    """One skill selected for offline summary generation."""

    name: str
    skill_dir: str
    source: str


_SAFE_NAME_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_\-]{0,63}$")
_GITHUB_URL_RE = re.compile(
    r"^https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?(?:/(?:tree|blob)/([^/]+)(?:/(.+))?)?/?$"
)
_GITLAB_URL_RE = re.compile(
    r"^https?://gitlab\.com/([^/]+)/([^/]+?)(?:\.git)?(?:/-/tree/([^/]+)(?:/(.+))?)?/?$"
)
_GIT_SSH_RE = re.compile(
    r"^git@([^:]+):([^/]+)/([^/]+?)(?:\.git)?$"
)


def _parse_github_url(url: str):
    """Parse a full GitHub URL into (owner, repo, branch, subpath).

    Returns None if the URL doesn't match.
    Supported formats:
      https://github.com/owner/repo
      https://github.com/owner/repo/tree/branch
      https://github.com/owner/repo/tree/branch/path/to/skill
      https://github.com/owner/repo/blob/branch/path/to/skill
    """
    m = _GITHUB_URL_RE.match(url.strip())
    if not m:
        return None
    owner, repo, branch, subpath = m.groups()
    return owner, repo, branch or "main", subpath


def _parse_gitlab_url(url: str):
    """Parse a GitLab URL into (owner, repo, branch, subpath).

    Returns None if the URL doesn't match.
    Supported formats:
      https://gitlab.com/owner/repo
      https://gitlab.com/owner/repo/-/tree/branch
      https://gitlab.com/owner/repo/-/tree/branch/path/to/skill
    """
    m = _GITLAB_URL_RE.match(url.strip())
    if not m:
        return None
    owner, repo, branch, subpath = m.groups()
    return owner, repo, branch or "main", subpath


def _parse_git_ssh_url(url: str):
    """Parse a git@ SSH URL into (host, owner, repo).

    Returns None if the URL doesn't match.
    Supported format: git@github.com:owner/repo.git
    """
    m = _GIT_SSH_RE.match(url.strip())
    if not m:
        return None
    host, owner, repo = m.groups()
    return host, owner, repo


def _clone_repo(git_url: str):
    """Shallow-clone a git repo and return (tmp_dir, repo_root).

    Requires git to be installed. The caller must clean up tmp_dir.
    """
    tmp_dir = tempfile.mkdtemp(prefix="zv-skill-")
    repo_dir = os.path.join(tmp_dir, "repo")
    try:
        import subprocess
        subprocess.run(
            ["git", "clone", "--depth", "1", git_url, repo_dir],
            check=True, capture_output=True, timeout=30,
        )
    except FileNotFoundError:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise RuntimeError("git is not installed")
    except Exception as e:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise RuntimeError(f"git clone failed: {e}")
    return tmp_dir, repo_dir


def _download_repo_zip(spec: str, branch: str = "main", host: str = "github", timeout: int = 30):
    """Download a GitHub/GitLab repo as zip and extract it.

    Returns (tmp_dir, repo_root) where tmp_dir is the temp directory to clean up
    and repo_root is the extracted repository root path.
    """
    if host == "gitlab":
        zip_url = f"https://gitlab.com/{spec}/-/archive/{branch}/{spec.split('/')[-1]}-{branch}.zip"
    else:
        zip_url = f"https://github.com/{spec}/archive/refs/heads/{branch}.zip"
    if isinstance(timeout, (list, tuple)):
        req_timeout = timeout
    else:
        req_timeout = (min(timeout, 5), timeout)
    resp = requests.get(zip_url, timeout=req_timeout, allow_redirects=True)
    resp.raise_for_status()

    tmp_dir = tempfile.mkdtemp(prefix="zv-skill-")
    zip_path = os.path.join(tmp_dir, "repo.zip")
    with open(zip_path, "wb") as f:
        f.write(resp.content)

    extract_dir = os.path.join(tmp_dir, "extracted")
    with zipfile.ZipFile(zip_path, "r") as zf:
        _safe_extractall(zf, extract_dir)

    # GitHub zips have a single top-level dir like "repo-main/"
    top_items = [d for d in os.listdir(extract_dir) if not d.startswith(".")]
    if len(top_items) == 1 and os.path.isdir(os.path.join(extract_dir, top_items[0])):
        return tmp_dir, os.path.join(extract_dir, top_items[0])
    return tmp_dir, extract_dir


def _download_github_dir(owner, repo, branch, subpath, dest_dir):
    """Download a subdirectory from GitHub using the Contents API.

    Recursively fetches all files under the given subpath and writes them
    to dest_dir. Used as a fallback when zip download fails.
    Costs one API request per directory (60/hr unauthenticated).
    """
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{subpath}?ref={branch}"
    resp = requests.get(api_url, timeout=30, headers={"Accept": "application/vnd.github.v3+json"})
    resp.raise_for_status()
    items = resp.json()

    if isinstance(items, dict):
        items = [items]

    for item in items:
        rel_path = item["path"]
        if subpath:
            rel_path = rel_path[len(subpath.strip("/")):].lstrip("/")
        local_path = os.path.join(dest_dir, rel_path)

        if item["type"] == "file":
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            dl_url = item.get("download_url")
            if not dl_url:
                continue
            file_resp = requests.get(dl_url, timeout=30)
            file_resp.raise_for_status()
            with open(local_path, "wb") as f:
                f.write(file_resp.content)
        elif item["type"] == "dir":
            os.makedirs(local_path, exist_ok=True)
            child_subpath = item["path"]
            _download_github_dir(owner, repo, branch, child_subpath, dest_dir)


# Directories to search for skills following the Agent Skills convention
_SKILL_SCAN_DIRS = [
    "skills",
    "skills/.curated",
    "skills/.experimental",
]

_SKILL_SCAN_SKIP = {
    "node_modules", "__pycache__", ".git", ".github", "venv", ".venv",
}


def _scan_skills_in_repo(repo_root: str) -> list:
    """Scan a repo for skill directories containing SKILL.md.

    Searches in conventional locations (skills/, skills/.curated/, etc.)
    and also checks the repo root itself.

    Returns a list of (skill_name, skill_dir_path) tuples.
    """
    found = []

    # Check repo root for a SKILL.md (single-skill repo)
    if os.path.isfile(os.path.join(repo_root, "SKILL.md")):
        fm = _parse_skill_frontmatter(_read_file_text(os.path.join(repo_root, "SKILL.md")))
        name = fm.get("name") or os.path.basename(repo_root)
        found.append((name, repo_root))
        return found

    for scan_dir in _SKILL_SCAN_DIRS:
        search_root = os.path.join(repo_root, scan_dir)
        if not os.path.isdir(search_root):
            continue
        for entry in os.listdir(search_root):
            if entry.startswith(".") and entry not in (".curated", ".experimental"):
                continue
            if entry in _SKILL_SCAN_SKIP:
                continue
            entry_path = os.path.join(search_root, entry)
            if os.path.isdir(entry_path) and os.path.isfile(os.path.join(entry_path, "SKILL.md")):
                fm = _parse_skill_frontmatter(
                    _read_file_text(os.path.join(entry_path, "SKILL.md"))
                )
                name = fm.get("name") or entry
                found.append((name, entry_path))

    return found


def _scan_skills_in_dir(directory: str) -> list:
    """Scan immediate subdirectories for SKILL.md files.

    Unlike _scan_skills_in_repo which checks conventional locations,
    this scans all direct children of the given directory.
    Returns a list of (skill_name, skill_dir_path) tuples.
    """
    found = []
    if not os.path.isdir(directory):
        return found
    for entry in os.listdir(directory):
        if entry.startswith(".") or entry in _SKILL_SCAN_SKIP:
            continue
        entry_path = os.path.join(directory, entry)
        if os.path.isdir(entry_path) and os.path.isfile(os.path.join(entry_path, "SKILL.md")):
            fm = _parse_skill_frontmatter(
                _read_file_text(os.path.join(entry_path, "SKILL.md"))
            )
            name = fm.get("name") or entry
            found.append((name, entry_path))
    return found


def _batch_install_skills(discovered, spec, skills_dir, source, result: InstallResult, display_name: str = ""):
    """Install a list of discovered skills into skills_dir."""
    single = len(discovered) == 1
    result.messages.append(f"Found {len(discovered)} skill(s) in {spec}:")
    for sname, sdir in discovered:
        safe_name = re.sub(r'[^a-zA-Z0-9_\-]', '-', sname)[:64]
        if not _SAFE_NAME_RE.match(safe_name):
            result.messages.append(f"  Skipping '{sname}' (invalid name)")
            continue
        target_dir = os.path.join(skills_dir, safe_name)
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        shutil.copytree(sdir, target_dir)
        _register_installed_skill(safe_name, source=source, display_name=display_name if single else "")
        result.installed.append(safe_name)
        result.messages.append(f"  + {safe_name}")

    if result.installed:
        result.messages.append(f"{len(result.installed)} skill(s) installed from {spec}.")
    else:
        result.messages.append("No valid skills found.")


def _read_file_text(path: str) -> str:
    """Read a file as UTF-8 text, returning empty string on failure."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def _install_local(path: str, result: InstallResult):
    """Install skill(s) from a local directory."""
    path = os.path.abspath(os.path.expanduser(path))
    if not os.path.isdir(path):
        raise SkillInstallError(f"'{path}' is not a directory.")

    skills_dir = get_skills_dir()
    os.makedirs(skills_dir, exist_ok=True)

    if os.path.isfile(os.path.join(path, "SKILL.md")):
        fm = _parse_skill_frontmatter(_read_file_text(os.path.join(path, "SKILL.md")))
        skill_name = fm.get("name") or os.path.basename(path)
        skill_name = re.sub(r'[^a-zA-Z0-9_\-]', '-', skill_name)[:64]
        _check_skill_name(skill_name)
        target_dir = os.path.join(skills_dir, skill_name)
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        shutil.copytree(path, target_dir)
        _register_installed_skill(skill_name, source="local")
        result.installed.append(skill_name)
        result.messages.append(f"Installed '{skill_name}' from local path.")
        return

    discovered = _scan_skills_in_repo(path) or _scan_skills_in_dir(path)
    if not discovered:
        raise SkillInstallError(f"No skills found in '{path}'.")

    _batch_install_skills(discovered, path, skills_dir, "local", result)


def _register_installed_skill(name: str, source: str = "zvhub", display_name: str = ""):
    """Register a newly installed skill into skills_config.json.

    source values: builtin, zvhub, github, clawhub, linkai, local, url
    """
    skills_dir = get_skills_dir()
    config_path = os.path.join(skills_dir, "skills_config.json")

    config = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception:
            config = {}

    if name in config:
        if display_name and not config[name].get("display_name"):
            config[name]["display_name"] = display_name
            try:
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=4, ensure_ascii=False)
            except Exception:
                pass
        return

    skill_dir = os.path.join(skills_dir, name)
    description = _read_skill_description(skill_dir) or ""

    entry = {
        "name": name,
        "description": description,
        "source": source,
        "enabled": True,
        "category": "skill",
    }
    if display_name:
        entry["display_name"] = display_name
    config[name] = entry

    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception:
        pass


def _parse_skill_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from SKILL.md content and return a dict with name/description."""
    result = {}
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return result
    for line in match.group(1).split('\n'):
        line = line.strip()
        for key in ('name', 'description'):
            if line.startswith(f'{key}:'):
                val = line[len(key) + 1:].strip()
                result[key] = val.strip('"').strip("'")
    return result


def _read_skill_description(skill_dir: str) -> str:
    """Read the description from a skill's SKILL.md frontmatter."""
    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.exists(skill_md):
        return ""
    try:
        with open(skill_md, "r", encoding="utf-8") as f:
            content = f.read()
        return _parse_skill_frontmatter(content).get("description", "")
    except Exception:
        return ""


def _iter_skill_dirs(root_dir: str) -> List[tuple]:
    """Return direct child skill directories under a root."""
    found = []
    if not os.path.isdir(root_dir):
        return found
    for entry in sorted(os.listdir(root_dir)):
        if entry.startswith(".") or entry in _SKILL_SCAN_SKIP:
            continue
        skill_dir = os.path.join(root_dir, entry)
        if os.path.isdir(skill_dir) and os.path.isfile(os.path.join(skill_dir, "SKILL.md")):
            found.append((entry, skill_dir))
    return found


def _resolve_summary_targets(
    name: Optional[str],
    *,
    include_builtin: bool,
    include_custom: bool,
) -> List[SkillSummaryTarget]:
    """Resolve skill directories to summarize, preferring custom over builtin."""

    targets: List[SkillSummaryTarget] = []
    seen = set()

    if name:
        _validate_skill_name(name)
        candidates = []
        if include_custom:
            candidates.append(("custom", os.path.join(get_skills_dir(), name)))
        if include_builtin:
            candidates.append(("builtin", os.path.join(get_builtin_skills_dir(), name)))
        for source, skill_dir in candidates:
            if os.path.isfile(os.path.join(skill_dir, "SKILL.md")):
                return [SkillSummaryTarget(name=name, skill_dir=skill_dir, source=source)]
        raise SkillInstallError(f"Skill '{name}' not found.")

    ordered_roots = []
    if include_custom:
        ordered_roots.append(("custom", get_skills_dir()))
    if include_builtin:
        ordered_roots.append(("builtin", get_builtin_skills_dir()))

    for source, root_dir in ordered_roots:
        for skill_name, skill_dir in _iter_skill_dirs(root_dir):
            if skill_name in seen:
                continue
            seen.add(skill_name)
            targets.append(
                SkillSummaryTarget(name=skill_name, skill_dir=skill_dir, source=source)
            )

    return targets


def _load_runtime_config():
    """Load config.json so model-backed summarization can reuse current provider settings."""
    ensure_sys_path()
    from config import load_config

    project_root = get_project_root()
    previous_cwd = os.getcwd()
    try:
        os.chdir(project_root)
        load_config()
    finally:
        os.chdir(previous_cwd)


def _run_skill_summary_generation(
    targets: List[SkillSummaryTarget],
    *,
    force: bool,
    dry_run: bool,
    model_override: Optional[str],
) -> List[dict]:
    """Generate summaries for one or more resolved skill targets."""

    ensure_sys_path()
    from agent.skills.summary import write_skill_summary
    from agent.skills.summary_generator import generate_skill_summary, get_skill_summary_path
    from bridge.agent_bridge import AgentLLMModel
    from bridge.bridge import Bridge
    from config import conf

    if model_override:
        conf()["model"] = model_override

    llm_model = AgentLLMModel(Bridge())
    model_name = str(conf().get("model") or "")
    provider_label = str(conf().get("bot_type") or llm_model._resolve_bot_type(model_name))

    results = []
    for target in targets:
        item = {
            "name": target.name,
            "source": target.source,
            "skill_dir": target.skill_dir,
            "summary_path": get_skill_summary_path(target.skill_dir),
            "ok": False,
            "skipped": False,
            "warnings": [],
            "error": None,
        }
        try:
            generation = generate_skill_summary(
                target.skill_dir,
                llm_model=llm_model,
                provider=provider_label,
                model_name=model_name,
                force=force,
            )
            item["skipped"] = generation.skipped
            if generation.validation:
                item["warnings"] = list(generation.validation.warnings)

            if not generation.skipped and generation.artifact and not dry_run:
                write_skill_summary(item["summary_path"], generation.artifact)

            item["ok"] = True
        except Exception as exc:
            item["error"] = str(exc)
        results.append(item)

    return results


def _install_url(url: str, result: InstallResult):
    """Install a skill from a direct SKILL.md URL."""
    result.messages.append(f"Downloading SKILL.md from {url} ...")
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        raise SkillInstallError(f"Failed to download SKILL.md: {e}")

    content = resp.text
    fm = _parse_skill_frontmatter(content)
    skill_name = fm.get("name")
    if not skill_name:
        raise SkillInstallError("SKILL.md missing 'name' field in frontmatter.")

    skill_name = skill_name.strip()
    _check_skill_name(skill_name)

    skills_dir = get_skills_dir()
    os.makedirs(skills_dir, exist_ok=True)
    skill_dir = os.path.join(skills_dir, skill_name)

    if os.path.isdir(skill_dir):
        result.messages.append(f"Skill '{skill_name}' already exists. Overwriting SKILL.md ...")
    os.makedirs(skill_dir, exist_ok=True)

    with open(os.path.join(skill_dir, "SKILL.md"), "w", encoding="utf-8") as f:
        f.write(content)

    _register_installed_skill(skill_name, source="url")
    result.installed.append(skill_name)
    result.messages.append(f"Installed '{skill_name}' from URL.")


def _install_archive_url(url: str, result: InstallResult):
    """Install skill(s) from a remote zip/tar.gz archive URL."""
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise SkillInstallError("Refusing to download from non-HTTPS URL.")

    filename = os.path.basename(parsed.path).split("?")[0]
    fallback_name = re.sub(r'\.(zip|tar\.gz|tgz)$', '', filename, flags=re.IGNORECASE)
    if not fallback_name or not _SAFE_NAME_RE.match(fallback_name):
        fallback_name = "skill-package"

    result.messages.append(f"Downloading archive from {url} ...")
    try:
        resp = requests.get(url, timeout=30, allow_redirects=True)
        resp.raise_for_status()
    except Exception as e:
        raise SkillInstallError(f"Failed to download archive: {e}")

    skills_dir = get_skills_dir()
    os.makedirs(skills_dir, exist_ok=True)

    content_type = resp.headers.get("Content-Type", "")
    lower_url = url.lower()

    if lower_url.endswith((".tar.gz", ".tgz")) or "gzip" in content_type:
        _install_targz_bytes(resp.content, fallback_name, skills_dir, result)
    else:
        _install_zip_bytes(resp.content, fallback_name, skills_dir, result=result, source_label="url")


def _install_targz_bytes(content: bytes, name: str, skills_dir: str, result: InstallResult):
    """Extract a tar.gz archive and install skill(s)."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tar_path = os.path.join(tmp_dir, "package.tar.gz")
        with open(tar_path, "wb") as f:
            f.write(content)

        import tarfile
        extract_dir = os.path.join(tmp_dir, "extracted")
        os.makedirs(extract_dir)
        with tarfile.open(tar_path, "r:gz") as tf:
            for member in tf.getmembers():
                resolved = os.path.realpath(os.path.join(extract_dir, member.name))
                if not resolved.startswith(os.path.realpath(extract_dir)):
                    raise SkillInstallError("Archive contains path traversal, aborting.")
            tf.extractall(extract_dir)

        top_items = [d for d in os.listdir(extract_dir) if not d.startswith(".")]
        pkg_root = extract_dir
        if len(top_items) == 1 and os.path.isdir(os.path.join(extract_dir, top_items[0])):
            pkg_root = os.path.join(extract_dir, top_items[0])

        discovered = _scan_skills_in_repo(pkg_root) or _scan_skills_in_dir(pkg_root)

        if discovered and len(discovered) > 1:
            _batch_install_skills(discovered, name, skills_dir, "url", result)
            return

        if discovered and len(discovered) == 1:
            sname, sdir = discovered[0]
            safe_name = re.sub(r'[^a-zA-Z0-9_\\-]', '-', sname)[:64]
            if not _SAFE_NAME_RE.match(safe_name):
                safe_name = name
            target = os.path.join(skills_dir, safe_name)
            if os.path.exists(target):
                shutil.rmtree(target)
            shutil.copytree(sdir, target)
            _register_installed_skill(safe_name, source="url")
            result.installed.append(safe_name)
            result.messages.append(f"Installed '{safe_name}' from URL.")
            return

        target = os.path.join(skills_dir, name)
        if os.path.exists(target):
            shutil.rmtree(target)
        shutil.copytree(pkg_root, target)
        _register_installed_skill(name, source="url")
        result.installed.append(name)
        result.messages.append(f"Installed '{name}' from URL.")


def _print_install_success(name: str, source: str):
    """Print a unified install success message with description and source."""
    skills_dir = get_skills_dir()
    config = load_skills_config()
    display = config.get(name, {}).get("display_name", "")
    desc = _read_skill_description(os.path.join(skills_dir, name))
    click.echo(click.style(f"✓ {name}", fg="green"))
    if display and display != name:
        click.echo(f"  名称: {display}")
    if desc:
        if len(desc) > 60:
            desc = desc[:57] + "…"
        click.echo(f"  描述: {desc}")
    click.echo(f"  来源: {source}")


def _validate_skill_name(name: str):
    """Reject names that contain path traversal or special characters."""
    if not _SAFE_NAME_RE.match(name):
        click.echo(
            f"Error: Invalid skill name '{name}'. "
            "Use only letters, digits, hyphens, and underscores.",
            err=True,
        )
        sys.exit(1)


def _validate_github_spec(spec: str):
    """Reject specs that don't look like owner/repo."""
    if not re.match(r"^[a-zA-Z0-9_\-]+/[a-zA-Z0-9_.\-]+$", spec):
        click.echo(f"Error: Invalid GitHub spec '{spec}'. Expected format: owner/repo", err=True)
        sys.exit(1)


def _check_skill_name(name: str):
    """Raise SkillInstallError if name is invalid."""
    if not _SAFE_NAME_RE.match(name):
        raise SkillInstallError(
            f"Invalid skill name '{name}'. Use only letters, digits, hyphens, and underscores."
        )


def _check_github_spec(spec: str):
    """Raise SkillInstallError if spec is not owner/repo."""
    if not re.match(r"^[a-zA-Z0-9_\-]+/[a-zA-Z0-9_.\-]+$", spec):
        raise SkillInstallError(f"Invalid GitHub spec '{spec}'. Expected format: owner/repo")


_JUNK_NAMES = {'.DS_Store', 'Thumbs.db', 'desktop.ini'}


def _is_junk_entry(filename: str) -> bool:
    parts = filename.replace('\\', '/').split('/')
    return any(p in _JUNK_NAMES or p == '__MACOSX' or p.startswith('._.') for p in parts)


def _safe_extractall(zf: zipfile.ZipFile, dest: str):
    """Extract zip while guarding against Zip Slip and filtering junk files."""
    dest = os.path.realpath(dest)
    members = []
    for member in zf.infolist():
        if _is_junk_entry(member.filename):
            continue
        target = os.path.realpath(os.path.join(dest, member.filename))
        if not target.startswith(dest + os.sep) and target != dest:
            raise ValueError(f"Unsafe zip entry detected: {member.filename}")
        members.append(member)
    zf.extractall(dest, members=members)


def _verify_checksum(content: bytes, expected: str):
    """Verify SHA-256 checksum of downloaded content.

    Returns True if checksum matches or no expected value provided.
    Exits with error if mismatch.
    """
    if not expected:
        return True
    actual = hashlib.sha256(content).hexdigest()
    if actual != expected.lower():
        click.echo(
            f"Error: Checksum mismatch!\n"
            f"  Expected: {expected}\n"
            f"  Actual:   {actual}\n"
            f"The downloaded package may have been tampered with.",
            err=True,
        )
        sys.exit(1)
    return True


def _check_checksum(content: bytes, expected: str):
    """Raise SkillInstallError on SHA-256 checksum mismatch."""
    if not expected:
        return
    actual = hashlib.sha256(content).hexdigest()
    if actual != expected.lower():
        raise SkillInstallError(
            f"Checksum mismatch! Expected: {expected}, Actual: {actual}. "
            "The downloaded package may have been tampered with."
        )


@click.group()
def skill():
    """Manage ZVAgent skills."""
    pass


# ------------------------------------------------------------------
# zv skill list
# ------------------------------------------------------------------
@skill.command("list")
@click.option("--remote", is_flag=True, help="Browse skills on Skill Hub")
@click.option("--page", default=1, type=int, help="Page number for remote listing")
def skill_list(remote, page):
    """List installed skills or browse Skill Hub."""
    if remote:
        _list_remote(page=page)
    else:
        _list_local()


def _list_local():
    """List locally installed skills."""
    config = load_skills_config()
    skills_dir = get_skills_dir()
    builtin_dir = get_builtin_skills_dir()

    # Merge builtin skills that are on disk but missing from config
    _merge_builtin_into_config(config, builtin_dir, skills_dir)

    if not config:
        click.echo("No skills installed.")
        return

    entries = sorted(config.values(), key=lambda x: x.get("name", ""))
    _print_skill_table(entries)


def _merge_builtin_into_config(config: dict, builtin_dir: str, skills_dir: str):
    """Scan builtin and custom dirs, add any new skills into config dict."""
    dirty = False
    for d, source in [(builtin_dir, "builtin"), (skills_dir, "custom")]:
        if not os.path.isdir(d):
            continue
        for name in os.listdir(d):
            if name.startswith(".") or name in ("skills_config.json",):
                continue
            skill_path = os.path.join(d, name)
            if not os.path.isdir(skill_path):
                continue
            if not os.path.isfile(os.path.join(skill_path, "SKILL.md")):
                continue
            if name in config:
                continue
            desc = _read_skill_description(skill_path)
            config[name] = {
                "name": name,
                "description": desc,
                "source": source,
                "enabled": True,
                "category": "skill",
            }
            dirty = True
    if dirty:
        config_path = os.path.join(skills_dir, "skills_config.json")
        try:
            os.makedirs(skills_dir, exist_ok=True)
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception:
            pass


def _print_skill_table(entries):
    """Print skills as a formatted table."""
    def _display_label(e):
        display = e.get("display_name", "")
        name = e.get("name", "")
        if display and display != name:
            return f"{display} ({name})"
        return name

    labels = [_display_label(e) for e in entries]
    name_w = max((len(l) for l in labels), default=4)
    name_w = max(name_w, 4) + 2
    desc_w = 40

    header = f"{'Name':<{name_w}} {'Status':<10} {'Source':<10} {'Description'}"
    click.echo(f"\n  Installed skills ({len(entries)})\n")
    click.echo(f"  {header}")
    click.echo(f"  {'─' * (name_w + 10 + 10 + desc_w)}")

    for e, label in zip(entries, labels):
        enabled = e.get("enabled", True)
        source = e.get("source", "")
        desc = e.get("description", "") or ""
        if len(desc) > desc_w:
            desc = desc[:desc_w - 3] + "..."

        status_icon = click.style("✓ on ", fg="green") if enabled else click.style("✗ off", fg="red")
        click.echo(f"  {label:<{name_w}} {status_icon}  {source:<10} {desc}")

    click.echo()


_REMOTE_PAGE_SIZE = 10


def _list_remote(page: int = 1):
    """List skills from remote Skill Hub with server-side pagination."""
    try:
        resp = requests.get(
            f"{SKILL_HUB_API}/skills",
            params={"page": page, "limit": _REMOTE_PAGE_SIZE},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        click.echo(f"Error: Failed to fetch from Skill Hub: {e}", err=True)
        sys.exit(1)

    skills = data.get("skills", [])
    total = data.get("total", len(skills))

    if not skills and page == 1:
        click.echo("No skills available on Skill Hub.")
        return

    total_pages = max(1, (total + _REMOTE_PAGE_SIZE - 1) // _REMOTE_PAGE_SIZE)
    page = min(page, total_pages)
    installed = set(load_skills_config().keys())

    name_w = max((len(s.get("name", "")) for s in skills), default=4)
    name_w = max(name_w, 4) + 2

    click.echo(f"\n  Skill Hub ({total} available) — page {page}/{total_pages}\n")
    click.echo(f"  {'Name':<{name_w}} {'Status':<12} {'Description'}")
    click.echo(f"  {'─' * (name_w + 12 + 50)}")

    for s in skills:
        name = s.get("name", "")
        desc = s.get("description", "") or s.get("display_name", "")
        if len(desc) > 50:
            desc = desc[:47] + "..."
        status = click.style("installed", fg="green") if name in installed else "—"
        click.echo(f"  {name:<{name_w}} {status:<12} {desc}")

    click.echo()
    nav_parts = []
    if page > 1:
        nav_parts.append(f"zv skill list --remote --page {page - 1}")
    if page < total_pages:
        nav_parts.append(f"zv skill list --remote --page {page + 1}")
    if nav_parts:
        click.echo(f"  Navigate: {' | '.join(nav_parts)}")
    click.echo(f"  Install:  zv skill install <name>")
    click.echo(f"  Browse:   https://skills.zvagent.ai\n")


# ------------------------------------------------------------------
# zv skill search
# ------------------------------------------------------------------
@skill.command()
@click.argument("query")
def search(query):
    """Search skills on Skill Hub."""
    try:
        resp = requests.get(f"{SKILL_HUB_API}/skills/search", params={"q": query}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        click.echo(f"Error: Failed to search Skill Hub: {e}", err=True)
        sys.exit(1)

    skills = data.get("skills", [])
    if not skills:
        click.echo(f'No skills found for "{query}".')
        return

    installed = set(load_skills_config().keys())
    name_w = max(len(s.get("name", "")) for s in skills)
    name_w = max(name_w, 4) + 2

    click.echo(f'\n  Search results for "{query}" ({len(skills)} found)\n')
    click.echo(f"  {'Name':<{name_w}} {'Status':<12} {'Description'}")
    click.echo(f"  {'─' * (name_w + 12 + 50)}")

    for s in skills:
        name = s.get("name", "")
        desc = s.get("description", "") or s.get("display_name", "")
        if len(desc) > 50:
            desc = desc[:47] + "..."
        status = click.style("installed", fg="green") if name in installed else "—"
        click.echo(f"  {name:<{name_w}} {status:<12} {desc}")

    click.echo(f"\n  Install with: zv skill install <name>\n")


# ------------------------------------------------------------------
# Core install function — reusable from CLI and chat plugin
# ------------------------------------------------------------------

def install_skill(name: str) -> InstallResult:
    """Core install logic, usable from CLI and chat plugin.

    Accepts all formats: Skill Hub name, owner/repo, GitHub/GitLab URL,
    git@ SSH, local path, SKILL.md URL.
    Returns InstallResult with installed skill names and messages.
    """
    result = InstallResult()
    try:
        _route_install(name, result)
    except SkillInstallError as e:
        result.error = str(e)
    return result


def _route_install(name: str, result: InstallResult):
    """Dispatch to the appropriate installer based on input format."""
    # --- Local path ---
    if name.startswith(("./", "../", "/", "~/")):
        _install_local(name, result)
        return

    # --- Direct SKILL.md URL ---
    if name.startswith(("http://", "https://")) and name.rstrip("/").endswith("SKILL.md"):
        dir_url = re.sub(r'/SKILL\.md/?$', '', name)
        gh = _parse_github_url(dir_url)
        if gh:
            owner, repo, branch, subpath = gh
            _install_github(f"{owner}/{repo}", result, subpath=subpath, skill_name=(
                subpath.rstrip("/").split("/")[-1] if subpath else repo
            ), branch=branch)
            return
        _install_url(name, result)
        return

    # --- Zip / tar.gz archive URL ---
    if name.startswith(("http://", "https://")) and re.search(r'\.(zip|tar\.gz|tgz)(\?.*)?$', name, re.IGNORECASE):
        _install_archive_url(name, result)
        return

    # --- Full GitHub URL ---
    parsed = _parse_github_url(name)
    if parsed:
        owner, repo, branch, subpath = parsed
        _install_github(f"{owner}/{repo}", result, subpath=subpath, branch=branch)
        return

    # --- Full GitLab URL ---
    gl = _parse_gitlab_url(name)
    if gl:
        owner, repo, branch, subpath = gl
        _install_gitlab(f"{owner}/{repo}", result, subpath=subpath, branch=branch)
        return

    # --- git@host:owner/repo.git SSH URL ---
    ssh = _parse_git_ssh_url(name)
    if ssh:
        host, owner, repo = ssh
        _install_git_clone(name, result, display_name=f"{owner}/{repo}")
        return

    # --- github: prefix ---
    if name.startswith("github:"):
        raw = name[7:]
        subpath = None
        if "#" in raw:
            raw, subpath = raw.split("#", 1)
        if re.match(r"^[a-zA-Z0-9_\-]+/[a-zA-Z0-9_.\-]+$", raw):
            _install_github(raw, result, subpath=subpath)
        else:
            _check_skill_name(raw)
            _install_hub(raw, result, provider="github")
        return

    # --- clawhub: prefix ---
    if name.startswith("clawhub:"):
        skill_name = name[8:]
        _check_skill_name(skill_name)
        _install_hub(skill_name, result, provider="clawhub")
        return

    # --- linkai: prefix ---
    if name.startswith("linkai:"):
        skill_code = name[7:]
        # LinkAI codes can be mixed-case alphanumeric; validate loosely
        if not re.match(r"^[a-zA-Z0-9_\-]{1,128}$", skill_code):
            raise SkillInstallError(f"Invalid LinkAI skill code '{skill_code}'.")
        _install_hub(skill_code, result, provider="linkai")
        return

    # --- owner/repo or owner/repo#subpath shorthand ---
    if re.match(r"^[a-zA-Z0-9_\-]+/[a-zA-Z0-9_.\-]+(?:#.+)?$", name):
        subpath = None
        spec = name
        if "#" in spec:
            spec, subpath = spec.split("#", 1)
        _install_github(spec, result, subpath=subpath)
        return

    # --- Fallback: Skill Hub by name ---
    _check_skill_name(name)
    _install_hub(name, result)


# ------------------------------------------------------------------
# zv skill install (CLI thin wrapper)
# ------------------------------------------------------------------
@skill.command()
@click.argument("name")
def install(name):
    """Install skill(s) from Skill Hub, GitHub, GitLab, git URL, or local path.

    When given an owner/repo (or full URL), downloads the repo and
    auto-discovers all skills/ subdirectories containing SKILL.md,
    installing them in batch. Use a subpath to install a single skill.

    Examples:

      zv skill install pptx                          (from Skill Hub)

      zv skill install larksuite/cli                 (GitHub shorthand, all skills)

      zv skill install larksuite/cli#skills/lark-im  (single skill by subpath)

      zv skill install https://github.com/owner/repo

      zv skill install https://gitlab.com/org/repo

      zv skill install git@github.com:owner/repo.git

      zv skill install ./my-local-skills             (local directory)

      zv skill install https://example.com/path/to/SKILL.md
    """
    result = install_skill(name)
    for msg in result.messages:
        click.echo(msg)
    if result.error:
        click.echo(f"Error: {result.error}", err=True)
        sys.exit(1)


# ------------------------------------------------------------------
# zv skill evolve
# ------------------------------------------------------------------
@skill.group()
def evolve():
    """Create, apply, and roll back conservative skill evolution proposals."""
    pass


@evolve.command("suggest")
@click.argument("name")
def evolve_suggest(name):
    """Inspect a skill and print improvement suggestions."""
    from cli.commands.skill_evolution import SkillEvolutionError, format_suggestions

    try:
        click.echo(format_suggestions(name))
    except SkillEvolutionError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@evolve.command("draft")
@click.argument("name")
def evolve_draft(name):
    """Create an editable proposal copy of a skill."""
    from cli.commands.skill_evolution import SkillEvolutionError, create_draft

    try:
        result = create_draft(name)
    except SkillEvolutionError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    click.echo(f"Created proposal: {result.proposal_id}")
    click.echo(f"Proposal dir: {result.proposal_dir}")
    click.echo(f"Edit this copy: {result.editable_skill_dir}")
    click.echo("")
    click.echo("Suggestions:")
    for item in result.suggestions:
        click.echo(f"  - {item}")
    click.echo("")
    click.echo(f"Apply after review: zv skill evolve apply {result.proposal_id}")


@evolve.command("list")
@click.argument("name", required=False)
def evolve_list(name=None):
    """List draft/applied evolution proposals."""
    from cli.commands.skill_evolution import list_proposals

    rows = list_proposals(name)
    if not rows:
        click.echo("No evolution proposals found.")
        return
    for row in rows:
        click.echo(f"{row['proposal_id']}  {row['skill_name']}  {row['status']}")
        click.echo(f"  {row['path']}")


@evolve.command("validate")
@click.argument("proposal_id")
def evolve_validate(proposal_id):
    """Validate a proposal's editable skill copy."""
    from cli.commands.skill_evolution import SkillEvolutionError, _find_proposal, validate_skill_dir

    try:
        proposal_dir = _find_proposal(proposal_id)
        result = validate_skill_dir(os.path.join(proposal_dir, "skill"))
    except SkillEvolutionError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    for warning in result.warnings:
        click.echo(f"Warning: {warning}")
    if not result.ok:
        for error in result.errors:
            click.echo(f"Error: {error}", err=True)
        sys.exit(1)
    click.echo("Validation passed.")


@evolve.command("apply")
@click.argument("proposal_id")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def evolve_apply(proposal_id, yes):
    """Apply a validated proposal, with automatic backup."""
    from cli.commands.skill_evolution import SkillEvolutionError, apply_proposal

    if not yes:
        click.confirm(
            "Apply this proposal and replace the live skill after creating a backup?",
            abort=True,
        )
    try:
        result = apply_proposal(proposal_id)
    except SkillEvolutionError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    click.echo(f"Applied proposal: {result.proposal_id}")
    click.echo(f"Skill: {result.skill_name}")
    click.echo(f"Backup: {result.backup_id}")
    click.echo(f"Live path: {result.target_dir}")
    for warning in result.warnings:
        click.echo(f"Warning: {warning}")
    click.echo(f"Rollback: zv skill evolve rollback {result.skill_name} --backup {result.backup_id}")


@evolve.command("backups")
@click.argument("name")
def evolve_backups(name):
    """List backups for a skill."""
    from cli.commands.skill_evolution import SkillEvolutionError, list_backups

    try:
        rows = list_backups(name)
    except SkillEvolutionError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    if not rows:
        click.echo(f"No backups found for skill '{name}'.")
        return
    for row in rows:
        click.echo(f"{row['backup_id']}")
        click.echo(f"  {row['path']}")


@evolve.command("rollback")
@click.argument("name")
@click.option("--backup", "backup_id", default=None, help="Backup id to restore; defaults to latest")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def evolve_rollback(name, backup_id, yes):
    """Restore a skill from a previous backup."""
    from cli.commands.skill_evolution import SkillEvolutionError, rollback_skill

    if not yes:
        click.confirm("Restore this skill from backup?", abort=True)
    try:
        result = rollback_skill(name, backup_id=backup_id)
    except SkillEvolutionError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    click.echo(f"Rolled back skill: {result.skill_name}")
    click.echo(f"Restored backup: {result.backup_id}")
    click.echo(f"Safety backup of replaced version: {result.safety_backup_id}")
    click.echo(f"Live path: {result.target_dir}")


def _install_hub(name, result: InstallResult, provider=None):
    """Install a skill from Skill Hub."""
    skills_dir = get_skills_dir()
    os.makedirs(skills_dir, exist_ok=True)

    result.messages.append(f"Fetching skill info for '{name}'...")

    try:
        body = {}
        if provider:
            body["provider"] = provider
        resp = requests.post(
            f"{SKILL_HUB_API}/skills/{name}/download",
            json=body,
            timeout=15,
        )
        resp.raise_for_status()
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            raise SkillInstallError(f"Skill '{name}' not found on Skill Hub.")
        raise SkillInstallError(f"Failed to fetch skill: {e}")
    except SkillInstallError:
        raise
    except Exception as e:
        raise SkillInstallError(f"Failed to connect to Skill Hub: {e}")

    content_type = resp.headers.get("Content-Type", "")
    hub_display_name = ""

    if "application/json" in content_type:
        data = resp.json()
        source_type = data.get("source_type")
        hub_display_name = data.get("display_name", "")

        if source_type == "github":
            source_url = data.get("source_url", "")
            has_mirror = data.get("has_mirror", False)
            gh_err = None

            gh_timeout = 15 if has_mirror else 30
            try:
                parsed_url = _parse_github_url(source_url)
                if parsed_url:
                    owner, repo, branch, subpath = parsed_url
                    _install_github(f"{owner}/{repo}", result, subpath=subpath, skill_name=name, branch=branch, timeout=gh_timeout)
                else:
                    _check_github_spec(source_url)
                    _install_github(source_url, result, skill_name=name, timeout=gh_timeout)
                if hub_display_name:
                    _register_installed_skill(name, display_name=hub_display_name)
                return
            except Exception as e:
                gh_err = e
                if not has_mirror:
                    raise SkillInstallError(f"GitHub download failed: {e}")

            # Fallback: download mirror from Skill Hub
            result.messages.append(f"GitHub download failed ({gh_err}), trying mirror...")
            try:
                mirror_resp = requests.post(
                    f"{SKILL_HUB_API}/skills/{name}/download",
                    json={"mirror": True},
                    timeout=30,
                )
                mirror_resp.raise_for_status()
            except Exception as e:
                raise SkillInstallError(
                    f"GitHub download failed ({gh_err}) and mirror also failed: {e}"
                )

            mirror_ct = mirror_resp.headers.get("Content-Type", "")
            if "application/zip" not in mirror_ct:
                raise SkillInstallError(
                    f"GitHub download failed ({gh_err}) and mirror returned unexpected content."
                )

            expected_checksum = mirror_resp.headers.get("X-Checksum-Sha256")
            _check_checksum(mirror_resp.content, expected_checksum)
            installed_before = len(result.installed)
            _install_zip_bytes(mirror_resp.content, name, skills_dir, result=result, source_label="zvhub", display_name=hub_display_name)
            if len(result.installed) == installed_before:
                _register_installed_skill(name, source="zvhub", display_name=hub_display_name)
                result.installed.append(name)
                result.messages.append(f"Installed '{name}' from mirror.")
            return

        if source_type == "registry":
            download_url = data.get("download_url")
            if download_url:
                parsed = urlparse(download_url)
                if parsed.scheme != "https":
                    raise SkillInstallError("Refusing to download from non-HTTPS URL.")
                src_provider = data.get("source_provider", "registry")
                has_mirror = data.get("has_mirror", False)
                expected_checksum = data.get("checksum") or data.get("sha256")
                result.messages.append(f"Source: {src_provider}")
                result.messages.append("Downloading skill package...")
                dl_err = None
                dl_timeout = 15 if has_mirror else 30
                try:
                    dl_resp = requests.get(
                        download_url,
                        timeout=(min(dl_timeout, 5), dl_timeout),
                        allow_redirects=True,
                    )
                    dl_resp.raise_for_status()
                except Exception as e:
                    dl_err = e
                    if not has_mirror:
                        raise SkillInstallError(f"Failed to download from {src_provider}: {e}")

                if dl_err is None:
                    _check_checksum(dl_resp.content, expected_checksum)
                    installed_before = len(result.installed)
                    _install_zip_bytes(dl_resp.content, name, skills_dir, result=result, source_label=src_provider, display_name=hub_display_name)
                    if len(result.installed) == installed_before:
                        _register_installed_skill(name, source=src_provider, display_name=hub_display_name)
                        result.installed.append(name)
                        result.messages.append(f"Installed '{name}' from {src_provider}.")
                    return

                # Fallback: download mirror from Skill Hub
                result.messages.append(f"Direct download failed ({dl_err}), trying mirror...")
                try:
                    mirror_resp = requests.post(
                        f"{SKILL_HUB_API}/skills/{name}/download",
                        json={"mirror": True},
                        timeout=30,
                    )
                    mirror_resp.raise_for_status()
                except Exception as e:
                    raise SkillInstallError(
                        f"Direct download failed ({dl_err}) and mirror also failed: {e}"
                    )
                mirror_ct = mirror_resp.headers.get("Content-Type", "")
                if "application/zip" not in mirror_ct:
                    raise SkillInstallError(
                        f"Direct download failed ({dl_err}) and mirror returned unexpected content."
                    )
                expected_checksum = mirror_resp.headers.get("X-Checksum-Sha256")
                _check_checksum(mirror_resp.content, expected_checksum)
                installed_before = len(result.installed)
                _install_zip_bytes(mirror_resp.content, name, skills_dir, result=result, source_label="zvhub", display_name=hub_display_name)
                if len(result.installed) == installed_before:
                    _register_installed_skill(name, source="zvhub", display_name=hub_display_name)
                    result.installed.append(name)
                    result.messages.append(f"Installed '{name}' from mirror.")
            else:
                raise SkillInstallError("Unsupported registry provider.")
            return

        if "redirect" in data:
            source_url = data.get("source_url", "")
            parsed_url = _parse_github_url(source_url)
            if parsed_url:
                owner, repo, branch, subpath = parsed_url
                _install_github(f"{owner}/{repo}", result, subpath=subpath, skill_name=name, branch=branch)
            else:
                _check_github_spec(source_url)
                _install_github(source_url, result, skill_name=name)
            if hub_display_name:
                _register_installed_skill(name, display_name=hub_display_name)
            return

    elif "application/zip" in content_type:
        result.messages.append("Downloading skill package...")
        expected_checksum = resp.headers.get("X-Checksum-Sha256")
        _check_checksum(resp.content, expected_checksum)
        installed_before = len(result.installed)
        _install_zip_bytes(resp.content, name, skills_dir, result=result, source_label="zvhub")
        if len(result.installed) == installed_before:
            _register_installed_skill(name)
            result.installed.append(name)
            result.messages.append(f"Installed '{name}' from Skill Hub.")
        return

    raise SkillInstallError("Unexpected response from Skill Hub.")


def _install_github(spec, result: InstallResult, subpath=None, skill_name=None, branch="main", source="github", timeout=30):
    """Install skill(s) from a GitHub repo.

    Strategy: zip download first (no API rate limit), Contents API as fallback.
    """
    if "#" in spec and not subpath:
        spec, subpath = spec.split("#", 1)

    _check_github_spec(spec)

    skills_dir = get_skills_dir()
    os.makedirs(skills_dir, exist_ok=True)
    owner, repo = spec.split("/", 1)

    result.messages.append(f"Downloading from GitHub: {spec} (branch: {branch})...")

    tmp_dir = None
    repo_root = None
    try:
        tmp_dir, repo_root = _download_repo_zip(spec, branch, timeout=timeout)
    except Exception:
        result.messages.append("Zip download failed, falling back to Contents API...")

    if repo_root:
        try:
            _install_from_repo_root(repo_root, spec, subpath, skill_name, skills_dir, source, result)
            return
        except SkillInstallError:
            raise
        except Exception as e:
            result.messages.append(f"Error processing zip: {e}")
            result.messages.append("Falling back to Contents API...")
        finally:
            if tmp_dir:
                shutil.rmtree(tmp_dir, ignore_errors=True)

    if not subpath:
        raise SkillInstallError(
            f"Zip download failed and batch install requires zip. "
            f"Try again or specify a subpath: {spec}#skills/<name>"
        )

    if not skill_name:
        skill_name = subpath.rstrip("/").split("/")[-1]
    _check_skill_name(skill_name)

    result.messages.append(f"Downloading via Contents API: {spec}/{subpath} ...")
    target_dir = os.path.join(skills_dir, skill_name)
    try:
        with tempfile.TemporaryDirectory() as api_tmp:
            api_dest = os.path.join(api_tmp, skill_name)
            os.makedirs(api_dest)
            _download_github_dir(owner, repo, branch, subpath.strip("/"), api_dest)
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir)
            shutil.copytree(api_dest, target_dir)
        _register_installed_skill(skill_name, source=source)
        result.installed.append(skill_name)
        result.messages.append(f"Installed '{skill_name}' from GitHub.")
    except Exception as e:
        raise SkillInstallError(f"Contents API also failed: {e}")


def _install_from_repo_root(repo_root, spec, subpath, skill_name, skills_dir, source, result: InstallResult):
    """Install skill(s) from an already-extracted repo root directory."""
    if subpath:
        source_dir = os.path.join(repo_root, subpath.strip("/"))
        if not os.path.isdir(source_dir):
            raise SkillInstallError(f"Path '{subpath}' not found in repository.")

        if os.path.isfile(os.path.join(source_dir, "SKILL.md")):
            if not skill_name:
                fm = _parse_skill_frontmatter(
                    _read_file_text(os.path.join(source_dir, "SKILL.md"))
                )
                skill_name = fm.get("name") or subpath.rstrip("/").split("/")[-1]
            _check_skill_name(skill_name)

            target_dir = os.path.join(skills_dir, skill_name)
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir)
            shutil.copytree(source_dir, target_dir)
            _register_installed_skill(skill_name, source=source)
            result.installed.append(skill_name)
            result.messages.append(f"Installed '{skill_name}' from {source}.")
            return

        discovered = _scan_skills_in_dir(source_dir)
        if discovered:
            _batch_install_skills(discovered, spec, skills_dir, source, result)
            return

        raise SkillInstallError(f"No SKILL.md found in '{subpath}' or its subdirectories.")
    else:
        discovered = _scan_skills_in_repo(repo_root)

        if not discovered:
            if skill_name:
                _check_skill_name(skill_name)
            else:
                skill_name = spec.split("/")[-1]
                _check_skill_name(skill_name)
            target_dir = os.path.join(skills_dir, skill_name)
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir)
            shutil.copytree(repo_root, target_dir)
            _register_installed_skill(skill_name, source=source)
            result.installed.append(skill_name)
            result.messages.append(f"Installed '{skill_name}' from {source}.")
            return

        _batch_install_skills(discovered, spec, skills_dir, source, result)


def _install_gitlab(spec, result: InstallResult, subpath=None, branch="main"):
    """Install skill(s) from a GitLab repo via zip download."""
    _check_github_spec(spec)

    skills_dir = get_skills_dir()
    os.makedirs(skills_dir, exist_ok=True)

    result.messages.append(f"Downloading from GitLab: {spec} (branch: {branch})...")

    try:
        tmp_dir, repo_root = _download_repo_zip(spec, branch, host="gitlab")
    except Exception as e:
        raise SkillInstallError(f"Failed to download from GitLab: {e}")

    try:
        _install_from_repo_root(repo_root, spec, subpath, None, skills_dir, "gitlab", result)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def _install_git_clone(git_url: str, result: InstallResult, display_name: str = ""):
    """Install skill(s) from any git URL via shallow clone."""
    skills_dir = get_skills_dir()
    os.makedirs(skills_dir, exist_ok=True)

    result.messages.append(f"Cloning {display_name or git_url} ...")

    try:
        tmp_dir, repo_root = _clone_repo(git_url)
    except RuntimeError as e:
        raise SkillInstallError(str(e))

    try:
        _install_from_repo_root(repo_root, display_name or git_url, None, None, skills_dir, "git", result)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def _install_zip_bytes(content, name, skills_dir, result: InstallResult = None, source_label: str = "zip", display_name: str = ""):
    """Extract a zip archive and install skill(s).

    Supports three scenarios:
      1. Root contains SKILL.md → single skill install
      2. Contains multiple skill dirs (skills/, or immediate children with SKILL.md) → batch install
      3. Fallback → treat the entire archive as a single skill named `name`
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        zip_path = os.path.join(tmp_dir, "package.zip")
        with open(zip_path, "wb") as f:
            f.write(content)

        extract_dir = os.path.join(tmp_dir, "extracted")
        with zipfile.ZipFile(zip_path, "r") as zf:
            _safe_extractall(zf, extract_dir)

        top_items = [d for d in os.listdir(extract_dir) if not d.startswith(".")]
        pkg_root = extract_dir
        if len(top_items) == 1 and os.path.isdir(os.path.join(extract_dir, top_items[0])):
            pkg_root = os.path.join(extract_dir, top_items[0])

        discovered = _scan_skills_in_repo(pkg_root) or _scan_skills_in_dir(pkg_root)

        if discovered and len(discovered) > 1 and result is not None:
            _batch_install_skills(discovered, name, skills_dir, source_label, result, display_name=display_name)
            return

        if discovered and len(discovered) == 1:
            sname, sdir = discovered[0]
            safe_name = re.sub(r'[^a-zA-Z0-9_\-]', '-', sname)[:64]
            if not _SAFE_NAME_RE.match(safe_name):
                safe_name = name
            target = os.path.join(skills_dir, safe_name)
            if os.path.exists(target):
                shutil.rmtree(target)
            shutil.copytree(sdir, target)
            _register_installed_skill(safe_name, source=source_label, display_name=display_name)
            if result is not None:
                result.installed.append(safe_name)
                result.messages.append(f"Installed '{safe_name}' from {source_label}.")
            return

        target = os.path.join(skills_dir, name)
        if os.path.exists(target):
            shutil.rmtree(target)
        shutil.copytree(pkg_root, target)




# ------------------------------------------------------------------
# zv skill uninstall
# ------------------------------------------------------------------
@skill.command()
@click.argument("name")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def uninstall(name, yes):
    """Uninstall a skill."""
    _validate_skill_name(name)
    skills_dir = get_skills_dir()
    skill_dir = os.path.join(skills_dir, name)

    if not os.path.exists(skill_dir):
        click.echo(f"Error: Skill '{name}' is not installed.", err=True)
        sys.exit(1)

    if not yes:
        click.confirm(f"Uninstall skill '{name}'?", abort=True)

    shutil.rmtree(skill_dir)

    config_path = os.path.join(skills_dir, "skills_config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            config.pop(name, None)
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

    click.echo(click.style(f"✓ Skill '{name}' uninstalled.", fg="green"))


# ------------------------------------------------------------------
# zv skill enable / disable
# ------------------------------------------------------------------
@skill.command()
@click.argument("name")
def enable(name):
    """Enable a skill."""
    _set_enabled(name, True)


@skill.command()
@click.argument("name")
def disable(name):
    """Disable a skill."""
    _set_enabled(name, False)


def _set_enabled(name, enabled):
    _validate_skill_name(name)
    skills_dir = get_skills_dir()
    config_path = os.path.join(skills_dir, "skills_config.json")

    if not os.path.exists(config_path):
        click.echo(f"Error: No skills config found.", err=True)
        sys.exit(1)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception as e:
        click.echo(f"Error: Failed to read skills config: {e}", err=True)
        sys.exit(1)

    if name not in config:
        click.echo(f"Error: Skill '{name}' not found in config.", err=True)
        sys.exit(1)

    config[name]["enabled"] = enabled
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

    state = "enabled" if enabled else "disabled"
    icon = "✓" if enabled else "✗"
    color = "green" if enabled else "yellow"
    click.echo(click.style(f"{icon} Skill '{name}' {state}.", fg=color))


# ------------------------------------------------------------------
# zv skill info
# ------------------------------------------------------------------
@skill.command()
@click.argument("name")
def info(name):
    """Show details about an installed skill."""
    _validate_skill_name(name)
    skills_dir = get_skills_dir()
    builtin_dir = get_builtin_skills_dir()

    skill_dir = None
    source = None
    config = load_skills_config()
    for d, src in [(skills_dir, "custom"), (builtin_dir, "builtin")]:
        candidate = os.path.join(d, name)
        if os.path.isdir(candidate):
            skill_dir = candidate
            source = config.get(name, {}).get("source") or src
            break

    if not skill_dir:
        click.echo(f"Error: Skill '{name}' not found.", err=True)
        sys.exit(1)

    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.exists(skill_md):
        click.echo(f"Skill directory: {skill_dir}")
        click.echo("No SKILL.md found.")
        return

    with open(skill_md, "r", encoding="utf-8") as f:
        content = f.read()

    config = load_skills_config()
    entry = config.get(name, {})
    enabled = entry.get("enabled", True)
    status_str = click.style("✓ enabled", fg="green") if enabled else click.style("✗ disabled", fg="red")

    display_name = entry.get("display_name", "")
    click.echo(f"\n  Skill: {name}")
    if display_name and display_name != name:
        click.echo(f"  Display: {display_name}")
    click.echo(f"  Source: {source}")
    click.echo(f"  Status: {status_str}")
    click.echo(f"  Path: {skill_dir}")
    click.echo(f"\n{'─' * 60}")

    # Show first ~30 lines of SKILL.md as a preview
    lines = content.split("\n")
    preview = "\n".join(lines[:30])
    click.echo(preview)
    if len(lines) > 30:
        click.echo(f"\n  ... ({len(lines) - 30} more lines, see {skill_md})")
    click.echo()


# ------------------------------------------------------------------
# zv skill summarize
# ------------------------------------------------------------------
@skill.command("summarize")
@click.argument("name", required=False)
@click.option("--all", "summarize_all", is_flag=True, help="Summarize all discovered skills.")
@click.option("--builtin", "builtin_only", is_flag=True, help="Only summarize builtin skills.")
@click.option("--custom", "custom_only", is_flag=True, help="Only summarize custom skills.")
@click.option("--force", is_flag=True, help="Regenerate even when the source hash is unchanged.")
@click.option("--dry-run", is_flag=True, help="Generate and validate summaries without writing files.")
@click.option("--model", "model_override", default=None, help="Temporarily override the configured model.")
def summarize(name, summarize_all, builtin_only, custom_only, force, dry_run, model_override):
    """Generate grounded SKILL.summary.json sidecars offline."""

    if not name and not summarize_all:
        click.echo("Error: Provide a skill name or use --all.", err=True)
        sys.exit(1)
    if name and summarize_all:
        click.echo("Error: Use either a skill name or --all, not both.", err=True)
        sys.exit(1)
    if builtin_only and custom_only:
        click.echo("Error: Choose only one of --builtin or --custom.", err=True)
        sys.exit(1)

    include_builtin = builtin_only or not custom_only
    include_custom = custom_only or not builtin_only

    try:
        targets = _resolve_summary_targets(
            name,
            include_builtin=include_builtin,
            include_custom=include_custom,
        )
    except SkillInstallError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    if not targets:
        click.echo("Error: No skills found to summarize.", err=True)
        sys.exit(1)

    _load_runtime_config()
    results = _run_skill_summary_generation(
        targets,
        force=force,
        dry_run=dry_run,
        model_override=model_override,
    )

    wrote = 0
    skipped = 0
    failed = 0
    for item in results:
        location = f"{item['name']} [{item['source']}]"
        if item["ok"] and item["skipped"]:
            skipped += 1
            click.echo(f"SKIP {location}: up-to-date")
            continue
        if item["ok"]:
            wrote += 1
            verb = "VALIDATED" if dry_run else "WROTE"
            click.echo(f"{verb} {location}: {item['summary_path']}")
            for warning in item["warnings"]:
                click.echo(f"  warning: {warning}")
            continue
        failed += 1
        click.echo(f"FAIL {location}: {item['error']}", err=True)

    click.echo(
        f"Summary generation complete: {wrote} succeeded, {skipped} skipped, {failed} failed."
    )
    if failed:
        sys.exit(1)
