"""Trading engine: bar loop, strategy, order execution."""

from __future__ import annotations

import logging
import time
from typing import Any

from src.api.auth import Auth, TknMgr
from src.api.bal import BalApi
from src.api.bar import BarApi
from src.api.cli import ApiCli
from src.api.ord import OrdApi
from src.api.ord_idem import OrdIdem
from src.core.cfg import Cfg, load_cfg
from src.core.log import init_log
from src.strat.base import Ctx, Sig, StratBase
from src.strat.loader import load_strat

log = logging.getLogger("kiwoom")


def _norm_stk(cd: str) -> str:
    s = cd.strip()
    if s.startswith("A") and len(s) > 1 and s[1:].isdigit():
        return s[1:]
    return s


class Engine:
    """Run a loaded strategy on a watchlist with REST bars and orders."""

    def __init__(
        self,
        cfg: Cfg,
        strat: StratBase,
        watchlist: list[str],
        *,
        interval_sec: float = 60.0,
        bar_n: int = 60,
        dry_run: bool = False,
        strat_params: dict[str, Any] | None = None,
    ) -> None:
        self.cfg = cfg
        self.strat = strat
        self.watchlist = watchlist
        self.interval_sec = interval_sec
        self.bar_n = bar_n
        self.dry_run = dry_run
        self.strat_params = strat_params or {}

        self._running = False
        self._inited = False
        self.cli = ApiCli(cfg)
        auth = Auth(cfg, cli=self.cli)
        self.tkn_mgr = TknMgr(auth)
        self.bar_api = BarApi(self.cli, self.tkn_mgr)
        self.bal_api = BalApi(self.cli, self.tkn_mgr)
        self.ord_idem = OrdIdem(OrdApi(self.cli, self.tkn_mgr))

    def _refresh_positions(self, ctx: Ctx) -> None:
        try:
            res = self.bal_api.get_day()
            ctx.positions = {
                _norm_stk(it.stk_cd): it.rmnd_qty
                for it in res.items
                if _norm_stk(it.stk_cd)
            }
        except Exception:
            log.exception("balance refresh failed")

    def _exec_sig(self, sig: Sig) -> bool:
        if self.dry_run:
            log.info("DRY_RUN %s %s %s qty=%s %s", sig.side, sig.stk_cd, sig.id, sig.qty, sig.why)
            return True
        if sig.side == "buy":
            out = self.ord_idem.buy_once(sig.id, sig.stk_cd, sig.qty)
        else:
            out = self.ord_idem.sell_once(sig.id, sig.stk_cd, sig.qty)
        log.info(
            "ORDER %s %s ord_no=%s dup=%s %s",
            sig.side,
            sig.stk_cd,
            out.res.ord_no,
            out.dup,
            sig.why,
        )
        return not out.dup

    def run_once(self) -> list[Sig]:
        """Single tick: refresh balance, run strategy per symbol, maybe order."""
        ctx = Ctx(
            mode=self.cfg.api.mode,
            params={
                "qty": 1,
                **self.strat_params,
            },
        )
        self._refresh_positions(ctx)
        if not self._inited:
            self.strat.on_init(ctx)
            self._inited = True

        fired: list[Sig] = []
        for stk in self.watchlist:
            ctx.params["stk_cd"] = stk
            try:
                bars = self.bar_api.get(stk, self.bar_n)
            except Exception:
                log.exception("bar fetch failed: %s", stk)
                continue
            sig = self.strat.on_bar(bars, ctx)
            if sig is None:
                continue
            if sig.side == "sell":
                hold = ctx.positions.get(stk, 0)
                if hold <= 0:
                    log.info("skip sell %s: no position", stk)
                    continue
                if sig.qty > hold:
                    sig = Sig(
                        id=sig.id,
                        side=sig.side,
                        stk_cd=sig.stk_cd,
                        qty=hold,
                        why=sig.why,
                    )
            self._exec_sig(sig)
            fired.append(sig)
        return fired

    def run(self, *, max_ticks: int | None = None) -> None:
        """Blocking loop until stop() or max_ticks."""
        init_log(log_dir=self.cfg.app.log_dir)
        self._running = True
        ticks = 0
        log.info(
            "engine start strat=%s watch=%s mode=%s dry=%s",
            self.strat.name,
            self.watchlist,
            self.cfg.api.mode,
            self.dry_run,
        )
        while self._running:
            self.run_once()
            ticks += 1
            if max_ticks is not None and ticks >= max_ticks:
                break
            if self._running:
                time.sleep(self.interval_sec)
        log.info("engine stop")

    def stop(self) -> None:
        self._running = False


def make_engine(
    strat_name: str,
    watchlist: list[str] | None = None,
    *,
    cfg: Cfg | None = None,
    dry_run: bool = False,
    strat_params: dict[str, Any] | None = None,
    strat_kw: dict[str, Any] | None = None,
    **eng_kw: Any,
) -> Engine:
    """Factory: load strategy by name and build Engine."""
    c = cfg or load_cfg()
    strat = load_strat(strat_name, **(strat_kw or {}))
    wl = watchlist or ["005930"]
    return Engine(
        c,
        strat,
        wl,
        dry_run=dry_run,
        strat_params=strat_params or {},
        **eng_kw,
    )


def smoke_engine_once(
    strat_name: str = "strat_dummy",
    *,
    dry_run: bool = True,
    force_mode: str = "mock",
) -> list[Sig]:
    """One engine tick without loop (5.5 dry-run verification)."""
    eng = make_engine(
        strat_name,
        ["005930"],
        cfg=load_cfg(force_mode=force_mode),
        dry_run=dry_run,
        strat_params={"stk_cd": "005930", "qty": 1},
    )
    return eng.run_once()
