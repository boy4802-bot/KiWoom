"""Trade safety limits (kill switch)."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.cfg import Cfg
from src.core.state import EngState, load_state, save_state


@dataclass(slots=True)
class SafeVerdict:
    ok: bool
    reason: str = ""


class Safe:
    """Daily order count and loss limit guard."""

    def __init__(self, cfg: Cfg, st: EngState | None = None) -> None:
        self.cfg = cfg
        self.st = st or load_state()
        self._roll_day()

    def _roll_day(self) -> None:
        today = EngState.today()
        if self.st.date != today:
            self.st.date = today
            self.st.order_count = 0
            self.st.day_start_evlt = 0
            save_state(self.st)

    def set_day_start_evlt(self, evlt_amt: int) -> None:
        if self.st.day_start_evlt == 0 and evlt_amt:
            self.st.day_start_evlt = evlt_amt
            save_state(self.st)

    def can_trade(self, *, cur_evlt_amt: int = 0) -> SafeVerdict:
        self._roll_day()
        max_ord = self.cfg.trade.max_orders_per_day
        if self.st.order_count >= max_ord:
            return SafeVerdict(False, f"일일 주문 한도 초과 ({self.st.order_count}/{max_ord})")

        if cur_evlt_amt > 0 and self.st.day_start_evlt > 0:
            base = self.st.day_start_evlt
            loss_pct = (base - cur_evlt_amt) / base * 100.0
            lim = self.cfg.trade.max_daily_loss_pct
            if loss_pct >= lim:
                return SafeVerdict(
                    False,
                    f"일일 손실 한도 ({loss_pct:.2f}% >= {lim}%)",
                )
        return SafeVerdict(True, "")

    def record_order(self) -> None:
        self._roll_day()
        self.st.order_count += 1
        save_state(self.st)
