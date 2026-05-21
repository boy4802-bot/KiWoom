"""Load strategy plugins from strategies/ folder."""

from __future__ import annotations

import importlib.util
import inspect
from pathlib import Path
from typing import Type

from src.strat.base import StratBase

_ROOT = Path(__file__).resolve().parents[2]
_STRAT_DIR = _ROOT / "strategies"


def _find_strat_cls(mod) -> Type[StratBase]:
    found: list[Type[StratBase]] = []
    for _, obj in inspect.getmembers(mod, inspect.isclass):
        if obj is StratBase or not issubclass(obj, StratBase):
            continue
        if inspect.isabstract(obj):
            continue
        found.append(obj)
    if len(found) != 1:
        names = [c.__name__ for c in found]
        raise ValueError(f"expected one StratBase subclass, found {names}")
    return found[0]


def load_strat(name: str, **kwargs) -> StratBase:
    """Load strategy by module name (e.g. 'strat_ma' -> strategies/strat_ma.py)."""
    stem = name.removesuffix(".py")
    path = _STRAT_DIR / f"{stem}.py"
    if not path.exists():
        raise FileNotFoundError(f"strategy not found: {path}")

    spec = importlib.util.spec_from_file_location(f"strategies.{stem}", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load strategy module: {name}")

    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    cls = _find_strat_cls(mod)
    return cls(**kwargs)


def list_strats() -> list[str]:
    """List available strategy module stems."""
    out: list[str] = []
    for p in sorted(_STRAT_DIR.glob("strat_*.py")):
        out.append(p.stem)
    return out
