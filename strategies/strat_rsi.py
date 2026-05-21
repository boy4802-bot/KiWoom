"""RSI overbought/oversold strategy."""

from __future__ import annotations

from src.api.bar import Bar
from src.strat.base import Ctx, Sig, StratBase


def _rsi(closes: list[float], period: int) -> float:
    if len(closes) < period + 1:
        return 50.0
    gains = 0.0
    losses = 0.0
    for i in range(-period, 0):
        d = closes[i] - closes[i - 1]
        if d >= 0:
            gains += d
        else:
            losses -= d
    if losses == 0:
        return 100.0
    rs = gains / losses
    return 100.0 - (100.0 / (1.0 + rs))


class StratRsi(StratBase):
    name = "strat_rsi"

    def __init__(
        self,
        *,
        period: int = 14,
        buy_below: float = 30.0,
        sell_above: float = 70.0,
    ) -> None:
        self.period = period
        self.buy_below = buy_below
        self.sell_above = sell_above
        self._last_bar_date = ""

    def on_init(self, ctx: Ctx) -> None:
        self._last_bar_date = ""

    def on_bar(self, bars: list[Bar], ctx: Ctx) -> Sig | None:
        need = self.period + 2
        if len(bars) < need:
            return None

        p = ctx.params
        period = int(p.get("rsi_period", self.period))
        buy_below = float(p.get("rsi_buy_below", self.buy_below))
        sell_above = float(p.get("rsi_sell_above", self.sell_above))

        stk = str(p.get("stk_cd", "005930"))
        last = bars[-1]
        if last.date == self._last_bar_date:
            return None

        closes = [b.close_pric for b in bars]
        val = _rsi(closes, period)
        qty = int(p.get("qty", 1))
        pos = ctx.positions.get(stk, 0)

        sig: Sig | None = None
        if val <= buy_below and pos <= 0:
            sig = Sig(
                id=f"rsi_{stk}_{last.date}_buy",
                side="buy",
                stk_cd=stk,
                qty=qty,
                why=f"RSI {val:.1f} <= {buy_below}",
            )
        elif val >= sell_above and pos > 0:
            sig = Sig(
                id=f"rsi_{stk}_{last.date}_sell",
                side="sell",
                stk_cd=stk,
                qty=min(qty, pos),
                why=f"RSI {val:.1f} >= {sell_above}",
            )

        if sig is not None:
            self._last_bar_date = last.date
        return sig
