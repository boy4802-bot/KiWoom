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
HogaCb = Callable[["RtHoga"], Awaitable[None] | None]
BalCb = Callable[["RtBal"], Awaitable[None] | None]
OrdCb = Callable[["RtOrd"], Awaitable[None] | None]


def _row_vals(row: dict[str, Any]) -> dict[str, Any]:
    vals = row.get("values") or {}
    return vals if isinstance(vals, dict) else {}


@dataclass(slots=True)
class RtCntr:
    """Parsed 0B (주식체결) real-time tick."""

    item: str
    tm: str
    cur_prc: str
    cntr_qty: str
    raw: dict[str, Any]


@dataclass(slots=True)
class RtHoga:
    """Parsed 0D (주식호가잔량)."""

    item: str
    tm: str
    ask1: str
    bid1: str
    ask1_qty: str
    bid1_qty: str
    raw: dict[str, Any]


@dataclass(slots=True)
class RtBal:
    """Parsed 04 (잔고)."""

    item: str
    values: dict[str, Any]
    raw: dict[str, Any]


@dataclass(slots=True)
class RtOrd:
    """Parsed 00 (주문체결/주문접수)."""

    item: str
    values: dict[str, Any]
    raw: dict[str, Any]


def _parse_cntr(row: dict[str, Any]) -> RtCntr:
    vals = _row_vals(row)
    return RtCntr(
        item=str(row.get("item", "")),
        tm=str(vals.get("20", "")),
        cur_prc=str(vals.get("10", "")),
        cntr_qty=str(vals.get("15", "")),
        raw=row,
    )


def _parse_hoga(row: dict[str, Any]) -> RtHoga:
    vals = _row_vals(row)
    return RtHoga(
        item=str(row.get("item", "")),
        tm=str(vals.get("21", "")),
        ask1=str(vals.get("41", "")),
        bid1=str(vals.get("51", "")),
        ask1_qty=str(vals.get("61", "")),
        bid1_qty=str(vals.get("71", "")),
        raw=row,
    )


def _parse_bal(row: dict[str, Any]) -> RtBal:
    return RtBal(
        item=str(row.get("item", "")),
        values=_row_vals(row),
        raw=row,
    )


def _parse_ord(row: dict[str, Any]) -> RtOrd:
    return RtOrd(
        item=str(row.get("item", "")),
        values=_row_vals(row),
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
        on_hoga: HogaCb | None = None,
        on_bal: BalCb | None = None,
        on_ord: OrdCb | None = None,
        reconnect_wait_s: float = 2.0,
        open_timeout_s: float = 10.0,
    ) -> None:
        self.cfg = cfg
        self.tkn_mgr = tkn_mgr
        self.uri = ws_url(cfg)
        self.on_msg = on_msg
        self.on_cntr = on_cntr
        self.on_hoga = on_hoga
        self.on_bal = on_bal
        self.on_ord = on_ord
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

    async def reg_stk(
        self,
        stk_cds: list[str],
        types: list[str],
        *,
        grp_no: str = "1",
        refresh: str = "1",
    ) -> None:
        """Register stock-scoped real-time (0B, 0D, ...)."""
        await self.reg(stk_cds, types, grp_no=grp_no, refresh=refresh)

    async def reg_acc(
        self,
        types: list[str],
        *,
        acc_no: str | None = None,
        grp_no: str = "2",
        refresh: str = "0",
    ) -> None:
        """Register account-scoped real-time (04=잔고, 00=주문)."""
        acc = (acc_no or self.cfg.api.acc_no).strip()
        if not acc:
            raise ValueError("ACC_NO is required for account real-time REG")
        await self.reg([acc], types, grp_no=grp_no, refresh=refresh)

    async def remove(
        self,
        items: list[str],
        types: list[str],
        *,
        grp_no: str = "1",
        refresh: str = "",
    ) -> None:
        """Unregister real-time items (REMOVE)."""
        await self.send(
            {
                "trnm": "REMOVE",
                "grp_no": grp_no,
                "refresh": refresh,
                "data": [{"item": items, "type": types}],
            }
        )

    async def remove_stk(
        self,
        stk_cds: list[str],
        types: list[str],
        *,
        grp_no: str = "1",
    ) -> None:
        """Remove stock-scoped subscriptions."""
        await self.remove(stk_cds, types, grp_no=grp_no)

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

        if trnm == "REAL":
            await self._dispatch_real(data)

        if self.on_msg is not None:
            cb = self.on_msg(data)
            if asyncio.iscoroutine(cb):
                await cb

    async def _dispatch_real(self, data: dict[str, Any]) -> None:
        for row in data.get("data", []) or []:
            if not isinstance(row, dict):
                continue
            typ = str(row.get("type", ""))
            cb = None
            if typ == "0B" and self.on_cntr is not None:
                cb = self.on_cntr(_parse_cntr(row))
            elif typ == "0D" and self.on_hoga is not None:
                cb = self.on_hoga(_parse_hoga(row))
            elif typ == "04" and self.on_bal is not None:
                cb = self.on_bal(_parse_bal(row))
            elif typ == "00" and self.on_ord is not None:
                cb = self.on_ord(_parse_ord(row))
            if cb is not None and asyncio.iscoroutine(cb):
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


class WsPool:
    """In-memory subscription pool with add/remove and reconnect restore."""

    def __init__(
        self,
        ws: WsCli,
        *,
        stk_types: list[str] | None = None,
        stk_grp: str = "1",
        acc_types: list[str] | None = None,
        acc_grp: str = "2",
    ) -> None:
        self.ws = ws
        self.stk_types = stk_types or ["0B", "0D"]
        self.stk_grp = stk_grp
        self.acc_types = acc_types or ["04", "00"]
        self.acc_grp = acc_grp
        self._stks: set[str] = set()
        self._acc_on = False

    def list_stk(self) -> list[str]:
        return sorted(self._stks)

    def has_acc(self) -> bool:
        return self._acc_on

    async def add_stk(self, stk_cd: str) -> bool:
        """Add one stock; returns True if newly added."""
        cd = stk_cd.strip()
        if not cd or cd in self._stks:
            return False
        self._stks.add(cd)
        if self.ws.connected:
            await self.ws.reg_stk([cd], self.stk_types, grp_no=self.stk_grp, refresh="1")
        return True

    async def remove_stk(self, stk_cd: str) -> bool:
        """Remove one stock; returns True if removed."""
        cd = stk_cd.strip()
        if cd not in self._stks:
            return False
        self._stks.discard(cd)
        if self.ws.connected:
            await self.ws.remove_stk([cd], self.stk_types, grp_no=self.stk_grp)
        return True

    async def enable_acc(self) -> None:
        if self._acc_on:
            return
        self._acc_on = True
        if self.ws.connected:
            await self.ws.reg_acc(self.acc_types, grp_no=self.acc_grp)

    async def sync_stk(self) -> None:
        """Replace stock group subscriptions from pool state."""
        if not self.ws.connected:
            return
        if not self._stks:
            return
        await self.ws.reg_stk(
            list(self._stks),
            self.stk_types,
            grp_no=self.stk_grp,
            refresh="0",
        )

    async def connect(self) -> None:
        """Connect WebSocket and restore pool subscriptions."""
        await self.ws.connect()
        if self._stks:
            await self.sync_stk()
        if self._acc_on:
            await self.ws.reg_acc(self.acc_types, grp_no=self.acc_grp, refresh="0")

    async def close(self) -> None:
        await self.ws.close()


async def smoke_pool(
    cfg: Cfg | None = None,
    wait_s: float = 4.0,
) -> dict[str, dict[str, int]]:
    """Add 2 stocks, remove 1; returns tick counts before/after remove."""
    from src.api.auth import Auth
    from src.core.cfg import load_cfg

    c = cfg or load_cfg(force_mode="mock")
    phase = 1
    before: dict[str, int] = {}
    after: dict[str, int] = {}

    async def on_cntr(evt: RtCntr) -> None:
        bucket = before if phase == 1 else after
        bucket[evt.item] = bucket.get(evt.item, 0) + 1

    ws = WsCli(c, TknMgr(Auth(c)), on_cntr=on_cntr)
    pool = WsPool(ws, stk_types=["0B"])
    await pool.connect()
    await pool.add_stk("005930")
    await pool.add_stk("000660")
    await asyncio.sleep(wait_s)
    phase = 2
    await pool.remove_stk("000660")
    await asyncio.sleep(wait_s)
    await pool.close()
    return {"before": before, "after": after}


async def smoke_rt(
    cfg: Cfg | None = None,
    stk_cd: str = "005930",
    wait_s: float = 5.0,
) -> dict[str, int]:
    """REG 0B/0D/04/00 and count events; for 4.3 verification."""
    from src.api.auth import Auth
    from src.core.cfg import load_cfg

    c = cfg or load_cfg(force_mode="mock")
    cnt = {"0B": 0, "0D": 0, "04": 0, "00": 0}

    async def _cntr(_: RtCntr) -> None:
        cnt["0B"] += 1

    async def _hoga(_: RtHoga) -> None:
        cnt["0D"] += 1

    async def _bal(_: RtBal) -> None:
        cnt["04"] += 1

    async def _ord(_: RtOrd) -> None:
        cnt["00"] += 1

    ws = WsCli(
        c,
        TknMgr(Auth(c)),
        on_cntr=_cntr,
        on_hoga=_hoga,
        on_bal=_bal,
        on_ord=_ord,
    )
    await ws.connect()
    await ws.reg_stk([stk_cd], ["0B", "0D"])
    await ws.reg_acc(["04", "00"])
    await asyncio.sleep(wait_s)
    await ws.close()
    return cnt


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
