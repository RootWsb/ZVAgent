"""Path helpers for workspace-scoped tools."""

import os

from common.utils import expand_path


def resolve_workspace_path(path: str, cwd: str) -> str:
    """Resolve a tool path against the workspace cwd."""
    if not path:
        return path

    if path.startswith("~"):
        return expand_path(path)

    if os.path.isabs(path):
        return path

    return os.path.abspath(os.path.join(cwd, path))
