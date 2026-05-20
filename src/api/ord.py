"""Order APIs (kt10000 and base models)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.api.auth import TknMgr
from src.api.cli import ApiCli
from src.api.err import ensure_ok


@dataclass(slots=True)
class OrdRes:
    ord_no: str
    dmst_stex_tp: str


@dataclass(slots=True)
class OrdStat:
    ord_no: str
    orig_ord_no: str
    stk_cd: str
    stk_nm: str
    trde_tp: str
    io_tp_nm: str
    ord_qty: str
    cntr_qty: str
    ord_uv: str
    cntr_uv: str
    cntr_tm: str
    acpt_tp: str
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

    def get_prst(
        self,
        *,
        ord_dt: str = "",
        stk_bond_tp: str = "0",
        mrkt_tp: str = "0",
        sell_tp: str = "0",
        qry_tp: str = "0",
        stk_cd: str = "",
        fr_ord_no: str = "",
        dmst_stex_tp: str = "KRX",
    ) -> list[OrdStat]:
        """계좌별주문체결현황요청 kt00009.

        qry_tp: 0=전체, 1=체결
        """
        tkn = self.tkn_mgr.get().val
        body = {
            "ord_dt": ord_dt,
            "stk_bond_tp": stk_bond_tp,
            "mrkt_tp": mrkt_tp,
            "sell_tp": sell_tp,
            "qry_tp": qry_tp,
            "stk_cd": stk_cd,
            "fr_ord_no": fr_ord_no,
            "dmst_stex_tp": dmst_stex_tp,
        }
        res = self.cli.req(
            method="POST",
            path="/api/dostk/acnt",
            api_id="kt00009",
            tkn=tkn,
            body=body,
        )
        ensure_ok("kt00009", res.code, res.msg)
        rows: list[dict[str, Any]] = (
            res.data.get("acnt_ord_cntr_prst_array")
            or res.data.get("acnt_ord_cntr_prst_a")
            or []
        )
        out: list[OrdStat] = []
        for x in rows:
            out.append(
                OrdStat(
                    ord_no=str(x.get("ord_no", "")),
                    orig_ord_no=str(x.get("orig_ord_no", "")),
                    stk_cd=str(x.get("stk_cd", "")),
                    stk_nm=str(x.get("stk_nm", "")),
                    trde_tp=str(x.get("trde_tp", "")),
                    io_tp_nm=str(x.get("io_tp_nm", "")),
                    ord_qty=str(x.get("ord_qty", "")),
                    cntr_qty=str(x.get("cntr_qty", "")),
                    ord_uv=str(x.get("ord_uv", "")),
                    cntr_uv=str(x.get("cntr_uv", "")),
                    cntr_tm=str(x.get("cntr_tm", "")),
                    acpt_tp=str(x.get("acpt_tp", "")),
                    dmst_stex_tp=str(x.get("dmst_stex_tp", "")),
                )
            )
        return out
