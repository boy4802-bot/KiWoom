"""Project configuration loader."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

import yaml
from dotenv import load_dotenv


@dataclass(slots=True)
class AppCfg:
    name: str = "KiWoom"
    log_dir: str = "logs"


@dataclass(slots=True)
class TradeCfg:
    max_orders_per_day: int = 50
    max_daily_loss_pct: float = 3.0


@dataclass(slots=True)
class ApiCfg:
    mode: str = "mock"
    appkey: str = ""
    secret: str = ""
    acc_no: str = ""
    base_url: str = "https://mockapi.kiwoom.com"


@dataclass(slots=True)
class Cfg:
    app: AppCfg
    trade: TradeCfg
    api: ApiCfg


def _base_url(mode: str) -> str:
    return "https://api.kiwoom.com" if mode == "live" else "https://mockapi.kiwoom.com"


def _read_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"config file must be a mapping: {path}")
    return data


def load_cfg(
    env_path: Path | None = None,
    yaml_path: Path | None = None,
) -> Cfg:
    """Load config from .env and YAML.

    Priority: .env > yaml > defaults.
    """
    root = Path(__file__).resolve().parents[2]
    env_p = env_path or (root / ".env")
    yml_p = yaml_path or (root / "config" / "default.yaml")

    load_dotenv(env_p, override=True)
    y = _read_yaml(yml_p)

    app_y = y.get("app", {}) if isinstance(y.get("app", {}), dict) else {}
    trd_y = y.get("trade", {}) if isinstance(y.get("trade", {}), dict) else {}

    mode = os.getenv("KIWOOM_MODE", "mock").strip().lower() or "mock"
    if mode not in {"mock", "live"}:
        raise ValueError("KIWOOM_MODE must be 'mock' or 'live'")

    app = AppCfg(
        name=str(app_y.get("name", "KiWoom")),
        log_dir=str(app_y.get("log_dir", "logs")),
    )
    trade = TradeCfg(
        max_orders_per_day=int(trd_y.get("max_orders_per_day", 50)),
        max_daily_loss_pct=float(trd_y.get("max_daily_loss_pct", 3.0)),
    )
    api = ApiCfg(
        mode=mode,
        appkey=os.getenv("KIWOOM_APPKEY", "").strip(),
        secret=os.getenv("KIWOOM_SECRET", "").strip(),
        acc_no=os.getenv("ACC_NO", "").strip(),
        base_url=_base_url(mode),
    )
    return Cfg(app=app, trade=trade, api=api)
