"""App paths: dev tree vs frozen exe vs user Documents."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def install_root() -> Path:
    """Directory where app.py / src live (or PyInstaller bundle)."""
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def user_root() -> Path:
    """Per-user config (Documents/KiWoom)."""
    docs = Path.home() / "Documents" / "KiWoom"
    if os.name == "nt":
        return docs
    return Path.home() / "KiWoom"


def ensure_user_dirs() -> Path:
    root = user_root()
    (root / "data").mkdir(parents=True, exist_ok=True)
    (root / "logs").mkdir(parents=True, exist_ok=True)
    return root


def env_file() -> Path:
    """Prefer user .env, fallback project .env."""
    u = user_root() / ".env"
    if u.exists():
        return u
    p = install_root() / ".env"
    if p.exists():
        return p
    ex = install_root() / ".env.example"
    if ex.exists() and not u.exists():
        ensure_user_dirs()
        u.write_text(ex.read_text(encoding="utf-8"), encoding="utf-8")
        return u
    return u


def config_yaml() -> Path:
    bundled = install_root() / "config" / "default.yaml"
    if bundled.exists():
        return bundled
    return install_root() / "config" / "default.yaml"


def data_dir() -> Path:
    if is_frozen():
        d = user_root() / "data"
        d.mkdir(parents=True, exist_ok=True)
        return d
    d = install_root() / "data"
    d.mkdir(parents=True, exist_ok=True)
    return d


def log_dir() -> Path:
    if is_frozen():
        d = user_root() / "logs"
        d.mkdir(parents=True, exist_ok=True)
        return d
    return install_root() / "logs"
