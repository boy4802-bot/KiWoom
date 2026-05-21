"""Persist engine runtime state for recovery."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

KST_FMT = "%Y%m%d"


@dataclass
class EngState:
    date: str = ""
    strat: str = ""
    watchlist: list[str] = field(default_factory=list)
    dry_run: bool = True
    running: bool = False
    order_count: int = 0
    day_start_evlt: int = 0
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def today(cls) -> str:
        return datetime.now().strftime(KST_FMT)


def state_path(root: Path | None = None) -> Path:
    base = root or Path(__file__).resolve().parents[2]
    p = base / "data"
    p.mkdir(parents=True, exist_ok=True)
    return p / "eng_state.json"


def load_state(path: Path | None = None) -> EngState:
    p = path or state_path()
    if not p.exists():
        return EngState(date=EngState.today())
    raw = json.loads(p.read_text(encoding="utf-8"))
    return EngState(
        date=str(raw.get("date", "")),
        strat=str(raw.get("strat", "")),
        watchlist=list(raw.get("watchlist", [])),
        dry_run=bool(raw.get("dry_run", True)),
        running=bool(raw.get("running", False)),
        order_count=int(raw.get("order_count", 0)),
        day_start_evlt=int(raw.get("day_start_evlt", 0)),
        extra=dict(raw.get("extra", {})),
    )


def save_state(st: EngState, path: Path | None = None) -> None:
    p = path or state_path()
    p.write_text(json.dumps(asdict(st), ensure_ascii=False, indent=2), encoding="utf-8")
