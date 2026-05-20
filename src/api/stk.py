"""Stock info APIs (ka10001)."""

from __future__ import annotations

from dataclasses import dataclass

from src.api.auth import TknMgr
from src.api.cli import ApiCli
from src.api.err import ensure_ok


@dataclass(slots=True)
class StkInfo:
    stk_cd: str
    stk_nm: str
    cur_prc: str
    pred_pre: str
    flu_rt: str
    trde_qty: str
    open_pric: str
    high_pric: str
    low_pric: str


class StkApi:
    def __init__(self, cli: ApiCli, tkn_mgr: TknMgr) -> None:
        self.cli = cli
        self.tkn_mgr = tkn_mgr

    def get_info(self, stk_cd: str) -> StkInfo:
        tkn = self.tkn_mgr.get().val
        res = self.cli.req(
            method="POST",
            path="/api/dostk/stkinfo",
            api_id="ka10001",
            tkn=tkn,
            body={"stk_cd": stk_cd},
        )
        ensure_ok("ka10001", res.code, res.msg)
        d = res.data
        return StkInfo(
            stk_cd=str(d.get("stk_cd", "")),
            stk_nm=str(d.get("stk_nm", "")),
            cur_prc=str(d.get("cur_prc", "")),
            pred_pre=str(d.get("pred_pre", "")),
            flu_rt=str(d.get("flu_rt", "")),
            trde_qty=str(d.get("trde_qty", "")),
            open_pric=str(d.get("open_pric", "")),
            high_pric=str(d.get("high_pric", "")),
            low_pric=str(d.get("low_pric", "")),
        )
