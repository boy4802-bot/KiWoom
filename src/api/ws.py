"""Kiwoom real-time WebSocket client (LOGIN, PING, reconnect)."""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

import websockets
from websockets.asyncio.client import ClientConnection, connect
from websockets.exceptions import ConnectionClosed

from src.api.auth import TknMgr
from src.core.cfg import Cfg

log = logging.getLogger("kiwoom")

MsgCb = Callable[[dict[str, Any]], Awaitable[None] | None]
CntrCb = Callable[["RtCntr"], Awaitable[None] | None]


@dataclass(slots=True)
class RtCntr:
    """Parsed 0B (주식체결) real-time tick."""

    item: str
    tm: str
    cur_prc: str
    cntr_qty: str
    raw: dict[str, Any]


def _parse_cntr(row: dict[str, Any]) -> RtCntr:
    vals = row.get("values") or {}
    if not isinstance(vals, dict):
        vals = {}
    return RtCntr(
        item=str(row.get("item", "")),
        tm=str(vals.get("20", "")),
        cur_prc=str(vals.get("10", "")),
        cntr_qty=str(vals.get("15", "")),
        raw=row,
    )


def ws_url(cfg: Cfg) -> str:
    """WebSocket endpoint for mock or live."""
    host = "api.kiwoom.com" if cfg.api.mode == "live" else "mockapi.kiwoom.com"
    return f"wss://{host}:10000/api/dostk/websocket"


class WsCli:
    """Async WebSocket client with login, PING echo, and auto-reconnect."""

    def __init__(
        self,
        cfg: Cfg,
        tkn_mgr: TknMgr,
        *,
        on_msg: MsgCb | None = None,
        on_cntr: CntrCb | None = None,
        reconnect_wait_s: float = 2.0,
        open_timeout_s: float = 10.0,
    ) -> None:
        self.cfg = cfg
        self.tkn_mgr = tkn_mgr
        self.uri = ws_url(cfg)
        self.on_msg = on_msg
        self.on_cntr = on_cntr
        self.reconnect_wait_s = reconnect_wait_s
        self.open_timeout_s = open_timeout_s

        self._ws: ClientConnection | None = None
        self._logged_in = False
        self._running = False
        self._recv_task: asyncio.Task[None] | None = None
        self._send_lock = asyncio.Lock()

    @property
    def connected(self) -> bool:
        return self._ws is not None and self._logged_in

    async def connect(self) -> None:
        """Open socket and send LOGIN."""
        await self._close_quiet()
        self._ws = await connect(self.uri, open_timeout=self.open_timeout_s)
        self._logged_in = False
        tkn = self.tkn_mgr.get().val
        await self.send({"trnm": "LOGIN", "token": tkn})
        ok = await self._wait_login()
        if not ok:
            await self._close_quiet()
            raise RuntimeError("WebSocket LOGIN failed")
        self._logged_in = True
        self._start_recv_task()
        log.info("WebSocket connected: %s", self.uri)

    async def reg(
        self,
        items: list[str],
        types: list[str],
        *,
        grp_no: str = "1",
        refresh: str = "1",
    ) -> None:
        """Register real-time items (e.g. type 0B = 체결)."""
        await self.send(
            {
                "trnm": "REG",
                "grp_no": grp_no,
                "refresh": refresh,
                "data": [{"item": items, "type": types}],
            }
        )

    async def send(self, msg: dict[str, Any] | str) -> None:
        """Send JSON message."""
        if self._ws is None:
            raise RuntimeError("WebSocket is not connected")
        raw = msg if isinstance(msg, str) else json.dumps(msg, ensure_ascii=False)
        async with self._send_lock:
            await self._ws.send(raw)

    async def run(self) -> None:
        """Receive loop with reconnect until close() is called."""
        self._running = True
        while self._running:
            try:
                if not self.connected:
                    await self.connect()
                if self._recv_task is not None:
                    await self._recv_task
            except ConnectionClosed:
                log.warning("WebSocket closed by server")
            except Exception:
                log.exception("WebSocket error")
            finally:
                self._logged_in = False
                await self._close_quiet()
            if self._running:
                await asyncio.sleep(self.reconnect_wait_s)

    async def close(self) -> None:
        """Stop receive loop and close socket."""
        self._running = False
        await self._close_quiet()

    async def _wait_login(self, timeout_s: float = 10.0) -> bool:
        if self._ws is None:
            return False
        try:
            raw = await asyncio.wait_for(self._ws.recv(), timeout=timeout_s)
        except TimeoutError:
            return False
        data = json.loads(raw)
        await self._handle_msg(data)
        return data.get("trnm") == "LOGIN" and int(data.get("return_code", -1)) == 0

    def _start_recv_task(self) -> None:
        if self._recv_task is None or self._recv_task.done():
            self._recv_task = asyncio.create_task(self._recv_loop())

    async def _recv_loop(self) -> None:
        if self._ws is None:
            return
        try:
            async for raw in self._ws:
                data = json.loads(raw)
                await self._handle_msg(data)
        except ConnectionClosed:
            self._logged_in = False
            raise

    async def _handle_msg(self, data: dict[str, Any]) -> None:
        trnm = str(data.get("trnm", ""))

        if trnm == "LOGIN":
            code = int(data.get("return_code", -1))
            if code != 0:
                log.error("WebSocket LOGIN failed: %s", data.get("return_msg", ""))
            return

        if trnm == "PING":
            await self.send(data)
            return

        if trnm == "REAL" and self.on_cntr is not None:
            for row in data.get("data", []) or []:
                if not isinstance(row, dict):
                    continue
                if str(row.get("type", "")) != "0B":
                    continue
                cb = self.on_cntr(_parse_cntr(row))
                if asyncio.iscoroutine(cb):
                    await cb

        if self.on_msg is not None:
            cb = self.on_msg(data)
            if asyncio.iscoroutine(cb):
                await cb

    async def _close_quiet(self) -> None:
        self._logged_in = False
        if self._recv_task is not None and not self._recv_task.done():
            self._recv_task.cancel()
            try:
                await self._recv_task
            except (asyncio.CancelledError, ConnectionClosed):
                pass
            self._recv_task = None
        if self._ws is not None:
            try:
                await self._ws.close()
            except Exception:
                pass
            self._ws = None


async def smoke_cntr(
    cfg: Cfg | None = None,
    stk_cd: str = "005930",
    wait_s: float = 5.0,
) -> int:
    """REG 0B and count ticks; for 4.2 verification."""
    from src.api.auth import Auth
    from src.core.cfg import load_cfg

    c = cfg or load_cfg(force_mode="mock")
    n = 0

    def _on(c: RtCntr) -> None:
        nonlocal n
        n += 1

    ws = WsCli(c, TknMgr(Auth(c)), on_cntr=_on)
    await ws.connect()
    await ws.reg([stk_cd], ["0B"])
    await asyncio.sleep(wait_s)
    await ws.close()
    return n


async def smoke_login(cfg: Cfg | None = None, hold_s: float = 3.0) -> bool:
    """Connect, login, wait briefly, reconnect once; for 4.1 verification."""
    from src.api.auth import Auth
    from src.core.cfg import load_cfg

    c = cfg or load_cfg(force_mode="mock")
    cli = WsCli(c, TknMgr(Auth(c)))
    await cli.connect()
    await asyncio.sleep(hold_s)
    await cli.close()

    cli2 = WsCli(c, TknMgr(Auth(c)))
    await cli2.connect()
    await cli2.close()
    return True
