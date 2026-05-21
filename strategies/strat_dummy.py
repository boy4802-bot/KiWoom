"""Dummy strategy for 5.1 interface tests."""

from __future__ import annotations

from src.api.bar import Bar
from src.strat.base import Ctx, Sig, StratBase


class StratDummy(StratBase):
    name = "strat_dummy"

    def __init__(self, *, side: str = "buy") -> None:
        self._side: str = side
        self._fired = False

    def on_bar(self, bars: list[Bar], ctx: Ctx) -> Sig | None:
        if self._fired or not bars:
            return None
        last = bars[-1]
        stk = ctx.params.get("stk_cd", "005930")
        self._fired = True
        return Sig(
            id=f"dummy_{stk}_{last.date}_{self._side}",
            side=self._side,  # type: ignore[arg-type]
            stk_cd=str(stk),
            qty=int(ctx.params.get("qty", 1)),
            why="dummy once",
        )
