"""Account APIs (ka00001)."""

from __future__ import annotations

from dataclasses import dataclass

from src.api.cli import ApiCli
from src.api.err import ensure_ok
from src.api.auth import TknMgr


@dataclass(slots=True)
class AccRes:
    acc_no: str


class AccApi:
    def __init__(self, cli: ApiCli, tkn_mgr: TknMgr) -> None:
        self.cli = cli
        self.tkn_mgr = tkn_mgr

    def get_acc_no(self) -> AccRes:
        tkn = self.tkn_mgr.get().val
        res = self.cli.req(
            method="POST",
            path="/api/dostk/acnt",
            api_id="ka00001",
            tkn=tkn,
            body={},
        )
        ensure_ok("ka00001", res.code, res.msg)
        return AccRes(acc_no=str(res.data.get("acctNo", "")))
