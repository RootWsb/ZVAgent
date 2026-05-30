#!/usr/bin/env python
"""Download legal open-access paper PDFs from common scholarly identifiers."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, Optional
from urllib.parse import quote, unquote, urlparse

import requests


DEFAULT_TIMEOUT = 30
DEFAULT_MAX_BYTES = 80 * 1024 * 1024
USER_AGENT = "ZVAgent paper-download/1.0 (+https://github.com/zhayujie/ZVAgent)"
FORBIDDEN_HOSTS = {"sci-hub.vg"}
FORBIDDEN_HOST_PREFIXES = ("sci-hub.", "www.sci-hub.")

DOI_RE = re.compile(r"(10\.\d{4,9}/[^\s\"<>]+)", re.IGNORECASE)
ARXIV_RE = re.compile(r"(?P<id>(?:\d{4}\.\d{4,5})(?:v\d+)?|[a-z\-]+(?:\.[A-Z]{2})?/\d{7}(?:v\d+)?)", re.IGNORECASE)
PMCID_RE = re.compile(r"\b(PMC\d+)\b", re.IGNORECASE)


@dataclass
class Candidate:
    source_type: str
    download_url: str
    filename_hint: str = ""
    metadata: Dict[str, Any] | None = None


def is_forbidden_source_url(value: str) -> bool:
    parsed = urlparse(value.strip())
    host = parsed.netloc.lower().split("@")[-1].split(":")[0]
    if not host:
        return False
    return host in FORBIDDEN_HOSTS or any(host.startswith(prefix) for prefix in FORBIDDEN_HOST_PREFIXES)


def normalize_doi(value: str) -> Optional[str]:
    text = unquote(value.strip())
    text = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^doi:\s*", "", text, flags=re.IGNORECASE)
    match = DOI_RE.search(text)
    if not match:
        return None
    doi = match.group(1).strip().rstrip(".,;)")
    return doi


def normalize_arxiv_id(value: str) -> Optional[str]:
    text = unquote(value.strip())
    parsed = urlparse(text)
    if parsed.netloc.lower().endswith("arxiv.org"):
        path = parsed.path.strip("/")
        for prefix in ("abs/", "pdf/", "html/"):
            if path.lower().startswith(prefix):
                path = path[len(prefix):]
                break
        path = path.removesuffix(".pdf")
        match = ARXIV_RE.fullmatch(path)
        return match.group("id") if match else None
    if text.lower().startswith("arxiv:"):
        text = text.split(":", 1)[1].strip()
    match = ARXIV_RE.fullmatch(text)
    return match.group("id") if match else None


def normalize_pmcid(value: str) -> Optional[str]:
    match = PMCID_RE.search(value.strip())
    return match.group(1).upper() if match else None


def is_probable_pdf_url(value: str) -> bool:
    parsed = urlparse(value.strip())
    if parsed.scheme not in ("http", "https"):
        return False
    return parsed.path.lower().endswith(".pdf")


def safe_filename(text: str, default: str = "paper") -> str:
    text = unquote(text or "").strip()
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^A-Za-z0-9._-]+", "_", text)
    text = re.sub(r"_+", "_", text)
    text = text.strip("._-")
    if not text:
        text = default
    if not text.lower().endswith(".pdf"):
        text += ".pdf"
    return text[:180]


def filename_from_url(url: str) -> str:
    name = Path(urlparse(url).path).name
    return safe_filename(name, "paper.pdf")


def unpaywall_lookup(doi: str, email: str, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    if not email or "@" not in email:
        raise ValueError("Unpaywall DOI lookup requires a real email via --email or UNPAYWALL_EMAIL.")
    url = f"https://api.unpaywall.org/v2/{quote(doi, safe='')}?email={quote(email)}"
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
    response.raise_for_status()
    return response.json()


def candidate_from_unpaywall(doi: str, email: str, timeout: int = DEFAULT_TIMEOUT) -> Candidate:
    data = unpaywall_lookup(doi, email=email, timeout=timeout)
    locations = []
    best = data.get("best_oa_location")
    if isinstance(best, dict):
        locations.append(best)
    for item in data.get("oa_locations") or []:
        if isinstance(item, dict) and item not in locations:
            locations.append(item)

    for location in locations:
        pdf_url = location.get("url_for_pdf") or ""
        landing_url = location.get("url") or location.get("url_for_landing_page") or ""
        download_url = pdf_url or landing_url
        if download_url:
            title = data.get("title") or doi
            metadata = {
                "doi": doi,
                "title": data.get("title"),
                "year": data.get("year"),
                "oa_status": data.get("oa_status"),
                "is_oa": data.get("is_oa"),
                "license": location.get("license"),
                "version": location.get("version"),
                "host_type": location.get("host_type"),
                "landing_page": location.get("url_for_landing_page"),
                "unpaywall": data,
            }
            return Candidate("unpaywall", download_url, safe_filename(title), metadata)

    raise ValueError(f"No legal open-access PDF/location found by Unpaywall for DOI {doi}.")


def build_candidate(identifier: str, email: str = "", timeout: int = DEFAULT_TIMEOUT) -> Candidate:
    value = identifier.strip()
    if is_forbidden_source_url(value):
        raise ValueError(
            "This source is not supported because it may bypass publisher access controls. "
            "Use DOI/arXiv/PMCID lookup to find legal open-access copies instead."
        )

    if is_probable_pdf_url(value):
        return Candidate("direct_pdf_url", value, filename_from_url(value), {"input": identifier})

    arxiv_id = normalize_arxiv_id(value)
    if arxiv_id:
        bare_id = re.sub(r"v\d+$", "", arxiv_id, flags=re.IGNORECASE)
        return Candidate(
            "arxiv",
            f"https://arxiv.org/pdf/{arxiv_id}.pdf",
            safe_filename(f"arxiv_{bare_id}.pdf"),
            {"arxiv_id": arxiv_id},
        )

    pmcid = normalize_pmcid(value)
    if pmcid:
        return Candidate(
            "pmc",
            f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/",
            safe_filename(f"{pmcid}.pdf"),
            {"pmcid": pmcid},
        )

    doi = normalize_doi(value)
    if doi:
        return candidate_from_unpaywall(doi, email=email, timeout=timeout)

    parsed = urlparse(value)
    if parsed.scheme in ("http", "https"):
        return Candidate("url", value, filename_from_url(value), {"input": identifier})

    raise ValueError(
        "Unsupported identifier. Provide a DOI, arXiv ID/URL, PMCID, PMC URL, or direct PDF URL."
    )


def iter_content(response: requests.Response) -> Iterable[bytes]:
    for chunk in response.iter_content(chunk_size=1024 * 64):
        if chunk:
            yield chunk


def download_candidate(
    candidate: Candidate,
    output_dir: Path,
    filename: str = "",
    max_bytes: int = DEFAULT_MAX_BYTES,
    timeout: int = DEFAULT_TIMEOUT,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / safe_filename(filename or candidate.filename_hint or filename_from_url(candidate.download_url))

    with requests.get(
        candidate.download_url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/pdf,*/*"},
        stream=True,
        timeout=timeout,
        allow_redirects=True,
    ) as response:
        response.raise_for_status()
        content_length = int(response.headers.get("Content-Length") or 0)
        if content_length and content_length > max_bytes:
            raise ValueError(f"Remote file is too large: {content_length} bytes > {max_bytes} bytes.")

        total = 0
        first = b""
        with output_path.open("wb") as handle:
            for chunk in iter_content(response):
                if not first:
                    first = chunk[:8]
                total += len(chunk)
                if total > max_bytes:
                    handle.close()
                    output_path.unlink(missing_ok=True)
                    raise ValueError(f"Download exceeded max size: {max_bytes} bytes.")
                handle.write(chunk)

    if output_path.stat().st_size == 0:
        output_path.unlink(missing_ok=True)
        raise ValueError("Downloaded file is empty.")
    return output_path


def write_metadata(path: Path, payload: Dict[str, Any]) -> Path:
    metadata_path = path.with_suffix(path.suffix + ".json")
    metadata_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return metadata_path


def result_payload(
    ok: bool,
    identifier: str,
    candidate: Optional[Candidate] = None,
    output_path: Optional[Path] = None,
    metadata_path: Optional[Path] = None,
    error: str = "",
) -> Dict[str, Any]:
    metadata = candidate.metadata if candidate and candidate.metadata else {}
    return {
        "ok": ok,
        "identifier": identifier,
        "source_type": candidate.source_type if candidate else None,
        "download_url": candidate.download_url if candidate else None,
        "output_path": str(output_path) if output_path else None,
        "metadata_path": str(metadata_path) if metadata_path else None,
        "oa_status": metadata.get("oa_status"),
        "license": metadata.get("license"),
        "version": metadata.get("version"),
        "error": error,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download legal open-access academic paper PDFs.")
    parser.add_argument("identifier", help="DOI, arXiv ID/URL, PMCID, PMC URL, direct PDF URL, or OA URL")
    parser.add_argument("--output-dir", default="papers", help="Directory for downloaded PDFs")
    parser.add_argument("--filename", default="", help="Optional output filename")
    parser.add_argument("--email", default=os.environ.get("UNPAYWALL_EMAIL", ""), help="Email for Unpaywall DOI lookup")
    parser.add_argument("--max-size-mb", type=int, default=80, help="Maximum download size in MB")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="HTTP timeout in seconds")
    parser.add_argument("--dry-run", action="store_true", help="Print candidate URL without downloading")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    candidate: Optional[Candidate] = None
    try:
        candidate = build_candidate(args.identifier, email=args.email, timeout=args.timeout)
        if args.dry_run:
            print(json.dumps(result_payload(True, args.identifier, candidate), ensure_ascii=False, indent=2))
            return 0

        output_path = download_candidate(
            candidate,
            Path(args.output_dir),
            filename=args.filename,
            max_bytes=args.max_size_mb * 1024 * 1024,
            timeout=args.timeout,
        )
        metadata_payload = {
            "identifier": args.identifier,
            "candidate": asdict(candidate),
            "output_path": str(output_path),
        }
        metadata_path = write_metadata(output_path, metadata_payload)
        print(json.dumps(result_payload(True, args.identifier, candidate, output_path, metadata_path), ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps(result_payload(False, args.identifier, candidate, error=str(exc)), ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
