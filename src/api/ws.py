"""Kiwoom real-time WebSocket client (LOGIN, PING, reconnect)."""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Awaitable, Callable
from typing import Any

import websockets
from websockets.asyncio.client import ClientConnection, connect
from websockets.exceptions import ConnectionClosed

from src.api.auth import TknMgr
from src.core.cfg import Cfg

log = logging.getLogger("kiwoom")

MsgCb = Callable[[dict[str, Any]], Awaitable[None] | None]


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
        reconnect_wait_s: float = 2.0,
        open_timeout_s: float = 10.0,
    ) -> None:
        self.cfg = cfg
        self.tkn_mgr = tkn_mgr
        self.uri = ws_url(cfg)
        self.on_msg = on_msg
        self.reconnect_wait_s = reconnect_wait_s
        self.open_timeout_s = open_timeout_s

        self._ws: ClientConnection | None = None
        self._logged_in = False
        self._running = False
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
        log.info("WebSocket connected: %s", self.uri)

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
                await self._recv_loop()
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

    async def _recv_loop(self) -> None:
        if self._ws is None:
            return
        async for raw in self._ws:
            data = json.loads(raw)
            await self._handle_msg(data)

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

        if self.on_msg is not None:
            cb = self.on_msg(data)
            if asyncio.iscoroutine(cb):
                await cb

    async def _close_quiet(self) -> None:
        self._logged_in = False
        if self._ws is not None:
            try:
                await self._ws.close()
            except Exception:
                pass
            self._ws = None


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
