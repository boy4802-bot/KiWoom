"""OAuth token helpers for Kiwoom REST API."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.api.cli import ApiCli
from src.core.cfg import Cfg


@dataclass(slots=True)
class Tkn:
    val: str
    typ: str
    exp_dt: str

    def exp_at(self) -> datetime:
        return datetime.strptime(self.exp_dt, "%Y%m%d%H%M%S")


class Auth:
    def __init__(self, cfg: Cfg, cli: ApiCli | None = None) -> None:
        self.cfg = cfg
        self.cli = cli or ApiCli(cfg)

    def issue(self) -> Tkn:
        """Issue OAuth token with au10001."""
        body = {
            "grant_type": "client_credentials",
            "appkey": self.cfg.api.appkey,
            "secretkey": self.cfg.api.secret,
        }
        res = self.cli.req(
            method="POST",
            path="/oauth2/token",
            api_id="au10001",
            body=body,
        )
        if res.code != 0:
            raise RuntimeError(f"token issue failed: {res.code} {res.msg}")

        data = res.data
        return Tkn(
            val=str(data.get("token", "")),
            typ=str(data.get("token_type", "bearer")),
            exp_dt=str(data.get("expires_dt", "")),
        )

