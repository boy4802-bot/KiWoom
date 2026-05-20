"""Quote APIs (ka10003, ka10004)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.api.auth import TknMgr
from src.api.cli import ApiCli
from src.api.err import ensure_ok


def _pick(d: dict[str, Any], keys: list[str]) -> str:
    for k in keys:
        if k in d and d[k] not in (None, ""):
            return str(d[k])
    return ""


def _best(d: dict[str, Any], side: str, field: str) -> str:
    """Pick the best available level key among 1~10."""
    for n in range(1, 11):
        k = f"{side}_{n}th_pre_{field}"
        if k in d and d[k] not in (None, ""):
            return str(d[k])
    for n in range(1, 11):
        k = f"{side}_{n}st_pre_{field}"
        if k in d and d[k] not in (None, ""):
            return str(d[k])
    return ""


@dataclass(slots=True)
class Cntr:
    tm: str
    cur_prc: str
    pred_pre: str
    pre_rt: str
    cntr_trde_qty: str
    acc_trde_qty: str
    stex_tp: str


@dataclass(slots=True)
class Hoga:
    tm: str
    ask1: str
    bid1: str
    ask1_qty: str
    bid1_qty: str
    raw: dict[str, Any]


class QteApi:
    def __init__(self, cli: ApiCli, tkn_mgr: TknMgr) -> None:
        self.cli = cli
        self.tkn_mgr = tkn_mgr

    def get_cntr(self, stk_cd: str) -> list[Cntr]:
        """체결정보요청 ka10003."""
        tkn = self.tkn_mgr.get().val
        res = self.cli.req(
            method="POST",
            path="/api/dostk/stkinfo",
            api_id="ka10003",
            tkn=tkn,
            body={"stk_cd": stk_cd},
        )
        ensure_ok("ka10003", res.code, res.msg)
        out: list[Cntr] = []
        for x in (res.data.get("cntr_infr", []) or []):
            out.append(
                Cntr(
                    tm=str(x.get("tm", "")),
                    cur_prc=str(x.get("cur_prc", "")),
                    pred_pre=str(x.get("pred_pre", "")),
                    pre_rt=str(x.get("pre_rt", "")),
                    cntr_trde_qty=str(x.get("cntr_trde_qty", "")),
                    acc_trde_qty=str(x.get("acc_trde_qty", "")),
                    stex_tp=str(x.get("stex_tp", "")),
                )
            )
        return out

    def get_hoga(self, stk_cd: str) -> Hoga:
        """주식호가요청 ka10004."""
        tkn = self.tkn_mgr.get().val
        res = self.cli.req(
            method="POST",
            path="/api/dostk/mrkcond",
            api_id="ka10004",
            tkn=tkn,
            body={"stk_cd": stk_cd},
        )
        ensure_ok("ka10004", res.code, res.msg)
        d = res.data
        return Hoga(
            tm=_pick(d, ["bid_req_base_tm", "tm"]),
            ask1=_best(d, "sel", "bid"),
            bid1=_best(d, "buy", "bid"),
            ask1_qty=_best(d, "sel", "req"),
            bid1_qty=_best(d, "buy", "req"),
            raw=d,
        )
