"""Smoke helpers for strategy signal tests (no orders)."""

from __future__ import annotations

from src.api.auth import Auth, TknMgr
from src.api.bal import BalApi
from src.api.bar import Bar, BarApi
from src.api.cli import ApiCli
from src.core.cfg import Cfg, load_cfg
from src.strat.base import Ctx, Sig
from src.strat.loader import load_strat


def _norm_stk(cd: str) -> str:
    s = cd.strip()
    if s.startswith("A") and len(s) > 1 and s[1:].isdigit():
        return s[1:]
    return s


def _positions_from_bal(bal_api) -> dict[str, int]:
    try:
        res = bal_api.get_day()
    except Exception:
        return {}
    out: dict[str, int] = {}
    for it in res.items:
        cd = _norm_stk(it.stk_cd)
        if cd:
            out[cd] = it.rmnd_qty
    return out


def demo_bars_ma_cross() -> list[Bar]:
    """Flat series then one spike bar to trigger MA golden cross."""
    bars: list[Bar] = []
    for i in range(29):
        bars.append(
            Bar(
                date=f"202605{i:02d}",
                open_pric=100,
                high_pric=101,
                low_pric=99,
                close_pric=100,
                trde_qty=1000,
                trde_prica=100_000,
            )
        )
    bars.append(
        Bar(
            date="20260529",
            open_pric=300,
            high_pric=301,
            low_pric=299,
            close_pric=300,
            trde_qty=1000,
            trde_prica=300_000,
        )
    )
    return bars


def demo_bars(n: int = 25, *, uptrend: bool = True) -> list[Bar]:
    """Synthetic bars for offline strategy tests."""
    out: list[Bar] = []
    for i in range(n):
        c = 100.0 + i * (2.0 if uptrend else -2.0)
        out.append(
            Bar(
                date=f"202605{i:02d}",
                open_pric=c - 1,
                high_pric=c + 1,
                low_pric=c - 2,
                close_pric=c,
                trde_qty=1000.0,
                trde_prica=c * 1000,
            )
        )
    return out


def signal_offline(
    strat_name: str,
    bars: list[Bar] | None = None,
    *,
    positions: dict[str, int] | None = None,
    **strat_kw,
) -> Sig | None:
    """Run on_bar without API (5.3/5.4 offline verification)."""
    bars = bars or demo_bars(30, uptrend=True)
    ctx = Ctx(
        mode="mock",
        positions=positions or {},
        params={"stk_cd": "005930", "qty": 1},
    )
    strat = load_strat(strat_name, **strat_kw)
    strat.on_init(ctx)
    return strat.on_bar(bars, ctx)


def signal_once(
    strat_name: str,
    stk_cd: str = "005930",
    *,
    cfg: Cfg | None = None,
    bar_n: int = 60,
    **strat_kw,
) -> Sig | None:
    """Fetch bars and run one on_bar (5.3/5.4 verification)."""
    c = cfg or load_cfg(force_mode="mock")
    cli = ApiCli(c)
    tm = TknMgr(Auth(c, cli=cli))
    bars = BarApi(cli, tm).get(stk_cd, bar_n)
    pos = _positions_from_bal(BalApi(cli, tm))
    ctx = Ctx(
        mode=c.api.mode,
        positions=pos,
        params={"stk_cd": stk_cd, "qty": 1},
    )
    strat = load_strat(strat_name, **strat_kw)
    strat.on_init(ctx)
    return strat.on_bar(bars, ctx)
