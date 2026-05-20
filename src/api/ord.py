"""Order APIs (kt10000 and base models)."""

from __future__ import annotations

from dataclasses import dataclass

from src.api.auth import TknMgr
from src.api.cli import ApiCli
from src.api.err import ensure_ok


@dataclass(slots=True)
class OrdRes:
    ord_no: str
    dmst_stex_tp: str


class OrdApi:
    def __init__(self, cli: ApiCli, tkn_mgr: TknMgr) -> None:
        self.cli = cli
        self.tkn_mgr = tkn_mgr

    def buy(
        self,
        stk_cd: str,
        qty: int,
        *,
        dmst_stex_tp: str = "KRX",
        trde_tp: str = "3",
        ord_uv: str = "",
        cond_uv: str = "",
    ) -> OrdRes:
        """주식 매수주문 kt10000.

        Default trde_tp=3 (시장가). Use small qty in tests.
        """
        tkn = self.tkn_mgr.get().val
        body = {
            "dmst_stex_tp": dmst_stex_tp,
            "stk_cd": stk_cd,
            "ord_qty": str(qty),
            "ord_uv": ord_uv,
            "trde_tp": trde_tp,
            "cond_uv": cond_uv,
        }
        res = self.cli.req(
            method="POST",
            path="/api/dostk/ordr",
            api_id="kt10000",
            tkn=tkn,
            body=body,
        )
        ensure_ok("kt10000", res.code, res.msg)
        return OrdRes(
            ord_no=str(res.data.get("ord_no", "")),
            dmst_stex_tp=str(res.data.get("dmst_stex_tp", dmst_stex_tp)),
        )
