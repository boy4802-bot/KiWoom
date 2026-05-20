"""Kiwoom REST API base client."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from src.api.err import HttpErr
from src.core.cfg import Cfg


@dataclass(slots=True)
class ApiRes:
    code: int
    msg: str
    data: dict[str, Any]
    status_code: int


class ApiCli:
    """Small wrapper for Kiwoom REST calls."""

    def __init__(self, cfg: Cfg, timeout_s: float = 10.0) -> None:
        self.cfg = cfg
        self.base_url = cfg.api.base_url.rstrip("/")
        self.timeout_s = timeout_s

    def mk_hdr(
        self,
        api_id: str,
        tkn: str = "",
        cont_yn: str = "N",
        next_key: str = "",
    ) -> dict[str, str]:
        hdr = {
            "Content-Type": "application/json;charset=UTF-8",
            "api-id": api_id,
            "cont-yn": cont_yn,
            "next-key": next_key,
        }
        if tkn:
            hdr["authorization"] = f"Bearer {tkn}"
        return hdr

    def req(
        self,
        method: str,
        path: str,
        api_id: str,
        *,
        tkn: str = "",
        body: dict[str, Any] | None = None,
        cont_yn: str = "N",
        next_key: str = "",
    ) -> ApiRes:
        url = f"{self.base_url}/{path.lstrip('/')}"
        hdr = self.mk_hdr(api_id=api_id, tkn=tkn, cont_yn=cont_yn, next_key=next_key)
        with httpx.Client(timeout=self.timeout_s) as cli:
            r = cli.request(method.upper(), url, headers=hdr, json=body)
        try:
            r.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise HttpErr(api_id=api_id, status_code=e.response.status_code, msg=str(e)) from e
        js = r.json() if r.content else {}
        code = int(js.get("return_code", 0))
        msg = str(js.get("return_msg", ""))
        return ApiRes(code=code, msg=msg, data=js, status_code=r.status_code)

    def ping(self) -> tuple[bool, int]:
        """Connection smoke check for base domain."""
        try:
            with httpx.Client(timeout=self.timeout_s) as cli:
                r = cli.get(self.base_url)
            # Even 4xx/5xx means DNS/TLS/network is alive.
            return (True, r.status_code)
        except httpx.HTTPError:
            return (False, 0)
