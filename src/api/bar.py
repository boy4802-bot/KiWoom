"""Bar/candle APIs (ka10005)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from src.api.auth import TknMgr
from src.api.cli import ApiCli
from src.api.err import ensure_ok


def _num(v: str) -> float:
    s = (v or "").replace(",", "").replace("+", "").strip()
    if not s:
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


@dataclass(slots=True)
class Bar:
    date: str
    open_pric: float
    high_pric: float
    low_pric: float
    close_pric: float
    trde_qty: float
    trde_prica: float


class BarApi:
    def __init__(self, cli: ApiCli, tkn_mgr: TknMgr) -> None:
        self.cli = cli
        self.tkn_mgr = tkn_mgr

    def get(self, stk_cd: str, n: int = 60) -> list[Bar]:
        tkn = self.tkn_mgr.get().val
        res = self.cli.req(
            method="POST",
            path="/api/dostk/mrkcond",
            api_id="ka10005",
            tkn=tkn,
            body={"stk_cd": stk_cd},
        )
        ensure_ok("ka10005", res.code, res.msg)
        rows = (res.data.get("stk_ddwkmm", []) or [])[:n]
        out: list[Bar] = []
        for x in rows:
            out.append(
                Bar(
                    date=str(x.get("date", "")),
                    open_pric=_num(str(x.get("open_pric", ""))),
                    high_pric=_num(str(x.get("high_pric", ""))),
                    low_pric=_num(str(x.get("low_pric", ""))),
                    close_pric=_num(str(x.get("close_pric", ""))),
                    trde_qty=_num(str(x.get("trde_qty", ""))),
                    trde_prica=_num(str(x.get("trde_prica", ""))),
                )
            )
        return out

    def to_df(self, bars: list[Bar]) -> pd.DataFrame:
        df = pd.DataFrame(
            [
                {
                    "date": b.date,
                    "open": b.open_pric,
                    "high": b.high_pric,
                    "low": b.low_pric,
                    "close": b.close_pric,
                    "volume": b.trde_qty,
                    "amount": b.trde_prica,
                }
                for b in bars
            ]
        )
        if not df.empty:
            df = df.sort_values("date").reset_index(drop=True)
        return df
