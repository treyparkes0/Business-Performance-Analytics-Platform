"""No credentials are committed, and ignore rules cover local secret files."""

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKEN_PATTERNS = (
    re.compile(r"dapi[0-9a-fA-F]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
)
SKIP_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache"}
SKIP_NAMES = {".env", "secrets.toml"}


def test_gitignore_covers_env_and_streamlit_secrets():
    text = (ROOT / ".gitignore").read_text()
    assert ".env" in text.splitlines() or any(line.strip() == ".env" for line in text.splitlines())
    assert "secrets.toml" in text
    assert ".streamlit/secrets.toml" in text
    tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
    assert ".env" not in tracked
    assert not any(path.endswith("secrets.toml") for path in tracked)


def test_tree_has_no_token_material():
    hits = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name in SKIP_NAMES:
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".pyc", ".parquet"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for pattern in TOKEN_PATTERNS:
            if pattern.search(text):
                hits.append(f"{path}: {pattern.pattern}")
    assert hits == []
