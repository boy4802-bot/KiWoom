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

    def _post(self, api_id: str, body: dict[str, str], dmst_stex_tp: str) -> OrdRes:
        tkn = self.tkn_mgr.get().val
        res = self.cli.req(
            method="POST",
            path="/api/dostk/ordr",
            api_id=api_id,
            tkn=tkn,
            body=body,
        )
        ensure_ok(api_id, res.code, res.msg)
        return OrdRes(
            ord_no=str(res.data.get("ord_no", "")),
            dmst_stex_tp=str(res.data.get("dmst_stex_tp", dmst_stex_tp)),
        )

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
        body = {
            "dmst_stex_tp": dmst_stex_tp,
            "stk_cd": stk_cd,
            "ord_qty": str(qty),
            "ord_uv": ord_uv,
            "trde_tp": trde_tp,
            "cond_uv": cond_uv,
        }
        return self._post("kt10000", body, dmst_stex_tp)

    def sell(
        self,
        stk_cd: str,
        qty: int,
        *,
        dmst_stex_tp: str = "KRX",
        trde_tp: str = "3",
        ord_uv: str = "",
        cond_uv: str = "",
    ) -> OrdRes:
        """주식 매도주문 kt10001."""
        body = {
            "dmst_stex_tp": dmst_stex_tp,
            "stk_cd": stk_cd,
            "ord_qty": str(qty),
            "ord_uv": ord_uv,
            "trde_tp": trde_tp,
            "cond_uv": cond_uv,
        }
        return self._post("kt10001", body, dmst_stex_tp)

    def mdfy(
        self,
        orig_ord_no: str,
        stk_cd: str,
        qty: int,
        mdfy_uv: str,
        *,
        dmst_stex_tp: str = "KRX",
        mdfy_cond_uv: str = "",
    ) -> OrdRes:
        """주식 정정주문 kt10002."""
        body = {
            "dmst_stex_tp": dmst_stex_tp,
            "orig_ord_no": orig_ord_no,
            "stk_cd": stk_cd,
            "mdfy_qty": str(qty),
            "mdfy_uv": mdfy_uv,
            "mdfy_cond_uv": mdfy_cond_uv,
        }
        return self._post("kt10002", body, dmst_stex_tp)

    def cncl(
        self,
        orig_ord_no: str,
        stk_cd: str,
        qty: int = 0,
        *,
        dmst_stex_tp: str = "KRX",
    ) -> OrdRes:
        """주식 취소주문 kt10003.

        qty=0 means cancel all remaining quantity.
        """
        body = {
            "dmst_stex_tp": dmst_stex_tp,
            "orig_ord_no": orig_ord_no,
            "stk_cd": stk_cd,
            "cncl_qty": str(qty),
        }
        return self._post("kt10003", body, dmst_stex_tp)
