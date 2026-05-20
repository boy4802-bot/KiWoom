"""Idempotent order guard — same signal places at most one order."""

from __future__ import annotations

from dataclasses import dataclass

from src.api.ord import OrdApi, OrdRes


@dataclass(slots=True)
class IdemRes:
    res: OrdRes
    dup: bool  # True when cached result returned (no new API call)


class OrdIdem:
    """Map signal id -> first order result to block duplicate submissions."""

    def __init__(self, ord_api: OrdApi) -> None:
        self.ord = ord_api
        self._map: dict[str, OrdRes] = {}

    def has(self, sig: str) -> bool:
        return sig in self._map

    def clear(self, sig: str | None = None) -> None:
        if sig is None:
            self._map.clear()
        else:
            self._map.pop(sig, None)

    def buy_once(
        self,
        sig: str,
        stk_cd: str,
        qty: int,
        *,
        dmst_stex_tp: str = "KRX",
        trde_tp: str = "3",
        ord_uv: str = "",
        cond_uv: str = "",
    ) -> IdemRes:
        if sig in self._map:
            return IdemRes(self._map[sig], dup=True)
        res = self.ord.buy(
            stk_cd,
            qty,
            dmst_stex_tp=dmst_stex_tp,
            trde_tp=trde_tp,
            ord_uv=ord_uv,
            cond_uv=cond_uv,
        )
        self._map[sig] = res
        return IdemRes(res, dup=False)

    def sell_once(
        self,
        sig: str,
        stk_cd: str,
        qty: int,
        *,
        dmst_stex_tp: str = "KRX",
        trde_tp: str = "3",
        ord_uv: str = "",
        cond_uv: str = "",
    ) -> IdemRes:
        if sig in self._map:
            return IdemRes(self._map[sig], dup=True)
        res = self.ord.sell(
            stk_cd,
            qty,
            dmst_stex_tp=dmst_stex_tp,
            trde_tp=trde_tp,
            ord_uv=ord_uv,
            cond_uv=cond_uv,
        )
        self._map[sig] = res
        return IdemRes(res, dup=False)
