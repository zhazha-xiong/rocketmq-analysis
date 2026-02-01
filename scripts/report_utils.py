import os
from datetime import datetime


def get_repo_root(current_file: str) -> str:
    return os.path.abspath(os.path.join(os.path.dirname(current_file), "..", ".."))


def write_text(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
