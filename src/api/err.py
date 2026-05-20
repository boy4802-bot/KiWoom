"""Common API error helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ApiErr(Exception):
    api_id: str
    code: int
    msg: str

    def __str__(self) -> str:
        return f"[{self.api_id}] code={self.code} msg={self.msg}"


@dataclass(slots=True)
class HttpErr(Exception):
    api_id: str
    status_code: int
    msg: str

    def __str__(self) -> str:
        return f"[{self.api_id}] http={self.status_code} msg={self.msg}"


def ensure_ok(api_id: str, code: int, msg: str) -> None:
    if code != 0:
        raise ApiErr(api_id=api_id, code=code, msg=msg)
