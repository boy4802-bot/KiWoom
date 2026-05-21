"""Read/write .env for Streamlit settings panel."""

from __future__ import annotations

from pathlib import Path

from src.core.paths import ensure_user_dirs, user_root

_ENV_KEYS = (
    "KIWOOM_MODE",
    "KIWOOM_APPKEY",
    "KIWOOM_SECRET",
    "ACC_NO",
    "KIWOOM_APPKEY_MOCK",
    "KIWOOM_SECRET_MOCK",
    "ACC_NO_MOCK",
    "KIWOOM_APPKEY_LIVE",
    "KIWOOM_SECRET_LIVE",
    "ACC_NO_LIVE",
)


def env_path(root: Path | None = None) -> Path:
    if root is not None:
        return root / ".env"
    ensure_user_dirs()
    return user_root() / ".env"


def load_env_file(path: Path | None = None) -> dict[str, str]:
    p = path or env_path()
    out: dict[str, str] = {k: "" for k in _ENV_KEYS}
    if not p.exists():
        return out
    for line in p.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        k = k.strip()
        if k in out:
            out[k] = v.strip()
    return out


def save_env_file(values: dict[str, str], path: Path | None = None) -> None:
    p = path or env_path()
    cur = load_env_file(p)
    cur.update({k: values.get(k, cur.get(k, "")) for k in _ENV_KEYS})
    lines = [
        "# Kiwoom REST API credentials",
        "# mode: mock | live",
        f"KIWOOM_MODE={cur['KIWOOM_MODE'] or 'mock'}",
        "",
        "# Legacy keys (fallback)",
        f"KIWOOM_APPKEY={cur['KIWOOM_APPKEY']}",
        f"KIWOOM_SECRET={cur['KIWOOM_SECRET']}",
        f"ACC_NO={cur['ACC_NO']}",
        "",
        "# Recommended mode-specific keys",
        f"KIWOOM_APPKEY_MOCK={cur['KIWOOM_APPKEY_MOCK']}",
        f"KIWOOM_SECRET_MOCK={cur['KIWOOM_SECRET_MOCK']}",
        f"ACC_NO_MOCK={cur['ACC_NO_MOCK']}",
        "",
        f"KIWOOM_APPKEY_LIVE={cur['KIWOOM_APPKEY_LIVE']}",
        f"KIWOOM_SECRET_LIVE={cur['KIWOOM_SECRET_LIVE']}",
        f"ACC_NO_LIVE={cur['ACC_NO_LIVE']}",
        "",
    ]
    p.write_text("\n".join(lines), encoding="utf-8")
