"""PyInstaller entry: start Streamlit UI."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def main() -> None:
    root = _root()
    os.chdir(root)
    app = root / "app.py"
    if not app.exists():
        print(f"app.py not found: {app}")
        sys.exit(1)
    sys.argv = [
        "streamlit",
        "run",
        str(app),
        "--server.headless",
        "false",
        "--browser.gatherUsageStats",
        "false",
    ]
    from streamlit.web import cli as stcli

    sys.exit(stcli.main())


if __name__ == "__main__":
    main()
