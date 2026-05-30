import os


def get_project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_runtime_dir() -> str:
    path = os.environ.get("ZVAGENT_RUNTIME_DIR")
    if not path:
        path = os.path.join(get_project_root(), "runtime")
    path = os.path.abspath(os.path.expanduser(path))
    os.makedirs(path, exist_ok=True)
    return path


def get_runtime_path(*parts: str) -> str:
    path = os.path.join(get_runtime_dir(), *parts)
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    return path
