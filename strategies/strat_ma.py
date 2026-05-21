"""Moving-average crossover strategy."""

from __future__ import annotations

from src.api.bar import Bar
from src.strat.base import Ctx, Sig, StratBase


class StratMa(StratBase):
    name = "strat_ma"

    def __init__(self, *, short: int = 5, long: int = 20) -> None:
        self.short = short
        self.long = long
        self._last_bar_date = ""

    def on_init(self, ctx: Ctx) -> None:
        self._last_bar_date = ""

    def on_bar(self, bars: list[Bar], ctx: Ctx) -> Sig | None:
        if len(bars) < self.long + 1:
            return None

        stk = str(ctx.params.get("stk_cd", "005930"))

        last = bars[-1]
        if last.date == self._last_bar_date:
            return None

        closes = [b.close_pric for b in bars]
        prev_s = sum(closes[-self.short - 1 : -1]) / self.short
        prev_l = sum(closes[-self.long - 1 : -1]) / self.long
        cur_s = sum(closes[-self.short :]) / self.short
        cur_l = sum(closes[-self.long :]) / self.long

        qty = int(ctx.params.get("qty", 1))
        pos = ctx.positions.get(stk, 0)

        sig: Sig | None = None
        if prev_s <= prev_l and cur_s > cur_l and pos <= 0:
            sig = Sig(
                id=f"ma_{stk}_{last.date}_buy",
                side="buy",
                stk_cd=stk,
                qty=qty,
                why=f"MA golden cross ({self.short}/{self.long})",
            )
        elif prev_s >= prev_l and cur_s < cur_l and pos > 0:
            sell_qty = min(qty, pos)
            sig = Sig(
                id=f"ma_{stk}_{last.date}_sell",
                side="sell",
                stk_cd=stk,
                qty=sell_qty,
                why=f"MA dead cross ({self.short}/{self.long})",
            )

        if sig is not None:
            self._last_bar_date = last.date
        return sig
