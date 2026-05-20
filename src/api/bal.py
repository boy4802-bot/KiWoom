"""Balance APIs (ka01690)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.api.auth import TknMgr
from src.api.cli import ApiCli
from src.api.err import ensure_ok


def _to_int(v: str) -> int:
    s = (v or "").replace(",", "").strip()
    if not s:
        return 0
    return int(float(s))


def _to_float(v: str) -> float:
    s = (v or "").replace(",", "").strip()
    if not s:
        return 0.0
    return float(s)


@dataclass(slots=True)
class BalItem:
    stk_cd: str
    stk_nm: str
    rmnd_qty: int
    buy_uv: int
    cur_prc: int
    evlt_amt: int
    evltv_prft: int
    prft_rt: float


@dataclass(slots=True)
class BalRes:
    dt: str
    tot_buy_amt: int
    tot_evlt_amt: int
    tot_evltv_prft: int
    tot_prft_rt: float
    dbst_bal: int
    day_stk_asst: int
    items: list[BalItem]


class BalApi:
    def __init__(self, cli: ApiCli, tkn_mgr: TknMgr) -> None:
        self.cli = cli
        self.tkn_mgr = tkn_mgr

    def get_day(self, qry_dt: str | None = None) -> BalRes:
        """Daily balance/profit rate (ka01690)."""
        if not qry_dt:
            qry_dt = datetime.now().strftime("%Y%m%d")
        tkn = self.tkn_mgr.get().val
        res = self.cli.req(
            method="POST",
            path="/api/dostk/acnt",
            api_id="ka01690",
            tkn=tkn,
            body={"qry_dt": qry_dt},
        )
        ensure_ok("ka01690", res.code, res.msg)
        d = res.data
        rows = d.get("day_bal_rt", []) or []
        items = [
            BalItem(
                stk_cd=str(x.get("stk_cd", "")),
                stk_nm=str(x.get("stk_nm", "")),
                rmnd_qty=_to_int(str(x.get("rmnd_qty", "0"))),
                buy_uv=_to_int(str(x.get("buy_uv", "0"))),
                cur_prc=_to_int(str(x.get("cur_prc", "0"))),
                evlt_amt=_to_int(str(x.get("evlt_amt", "0"))),
                evltv_prft=_to_int(str(x.get("evltv_prft", "0"))),
                prft_rt=_to_float(str(x.get("prft_rt", "0"))),
            )
            for x in rows
        ]
        return BalRes(
            dt=str(d.get("dt", "")),
            tot_buy_amt=_to_int(str(d.get("tot_buy_amt", "0"))),
            tot_evlt_amt=_to_int(str(d.get("tot_evlt_amt", "0"))),
            tot_evltv_prft=_to_int(str(d.get("tot_evltv_prft", "0"))),
            tot_prft_rt=_to_float(str(d.get("tot_prft_rt", "0"))),
            dbst_bal=_to_int(str(d.get("dbst_bal", "0"))),
            day_stk_asst=_to_int(str(d.get("day_stk_asst", "0"))),
            items=items,
        )
