"""Strategy base types: signal, context, and StratBase."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from src.api.bar import Bar

Side = Literal["buy", "sell"]


@dataclass(slots=True)
class Sig:
    """Trading signal emitted by a strategy (no API calls)."""

    id: str
    side: Side
    stk_cd: str
    qty: int
    why: str = ""


@dataclass(slots=True)
class Ctx:
    """Read-only environment for strategy decisions."""

    mode: str
    positions: dict[str, int] = field(default_factory=dict)
    params: dict[str, Any] = field(default_factory=dict)


class StratBase:
    """All strategies inherit this and implement on_bar."""

    name: str = "base"

    def on_init(self, ctx: Ctx) -> None:
        """Called once when the engine starts."""

    def on_bar(self, bars: list[Bar], ctx: Ctx) -> Sig | None:
        """Called each engine tick with latest OHLCV bars."""
        return None
