"""OAuth token helpers for Kiwoom REST API."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import time

import httpx

from src.api.cli import ApiCli
from src.core.cfg import Cfg


@dataclass(slots=True)
class Tkn:
    val: str
    typ: str
    exp_dt: str

    def exp_at(self) -> datetime:
        return datetime.strptime(self.exp_dt, "%Y%m%d%H%M%S")

    def is_expiring(self, sec: int = 300) -> bool:
        return self.exp_at() <= (datetime.now() + timedelta(seconds=sec))


class Auth:
    def __init__(self, cfg: Cfg, cli: ApiCli | None = None) -> None:
        self.cfg = cfg
        self.cli = cli or ApiCli(cfg)

    def issue(self, retry: int = 3, wait_s: float = 1.2) -> Tkn:
        """Issue OAuth token with au10001."""
        body = {
            "grant_type": "client_credentials",
            "appkey": self.cfg.api.appkey,
            "secretkey": self.cfg.api.secret,
        }
        last_err: Exception | None = None
        for i in range(retry):
            try:
                res = self.cli.req(
                    method="POST",
                    path="/oauth2/token",
                    api_id="au10001",
                    body=body,
                )
                break
            except httpx.HTTPStatusError as e:
                last_err = e
                if e.response.status_code == 429 and i < retry - 1:
                    time.sleep(wait_s * (i + 1))
                    continue
                raise
        else:
            raise RuntimeError(f"token issue failed after retries: {last_err}")

        if res.code != 0:
            raise RuntimeError(f"token issue failed: {res.code} {res.msg}")

        data = res.data
        return Tkn(
            val=str(data.get("token", "")),
            typ=str(data.get("token_type", "Bearer")),
            exp_dt=str(data.get("expires_dt", "")),
        )

    def revoke(self, tkn: str) -> None:
        """Revoke OAuth token with au10002."""
        body = {
            "appkey": self.cfg.api.appkey,
            "secretkey": self.cfg.api.secret,
            "token": tkn,
        }
        res = self.cli.req(
            method="POST",
            path="/oauth2/revoke",
            api_id="au10002",
            tkn=tkn,
            body=body,
        )
        if res.code != 0:
            raise RuntimeError(f"token revoke failed: {res.code} {res.msg}")


class TknMgr:
    """Cache token and re-issue before expiry."""

    def __init__(self, auth: Auth, refresh_sec: int = 300) -> None:
        self.auth = auth
        self.refresh_sec = refresh_sec
        self._cur: Tkn | None = None

    def get(self) -> Tkn:
        if self._cur is None or self._cur.is_expiring(self.refresh_sec):
            self._cur = self.auth.issue()
        return self._cur

    def rotate(self) -> Tkn:
        """Force revoke current token then issue a new one."""
        if self._cur is not None and self._cur.val:
            self.auth.revoke(self._cur.val)
        self._cur = self.auth.issue()
        return self._cur

