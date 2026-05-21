"""Project configuration loader."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

import yaml
from dotenv import load_dotenv

from src.core.paths import config_yaml, env_file, log_dir


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


def _pick_mode_val(mode: str, base: str) -> str:
    """Pick mode-specific env value, fallback to legacy key."""
    mode_key = f"{base}_{mode.upper()}"
    return os.getenv(mode_key, "").strip() or os.getenv(base, "").strip()


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
    force_mode: str | None = None,
) -> Cfg:
    """Load config from .env and YAML.

    Priority: .env > yaml > defaults.
    """
    env_p = env_path or env_file()
    yml_p = yaml_path or config_yaml()

    load_dotenv(env_p, override=True)
    y = _read_yaml(yml_p)

    app_y = y.get("app", {}) if isinstance(y.get("app", {}), dict) else {}
    trd_y = y.get("trade", {}) if isinstance(y.get("trade", {}), dict) else {}

    mode = (force_mode or os.getenv("KIWOOM_MODE", "mock")).strip().lower() or "mock"
    if mode not in {"mock", "live"}:
        raise ValueError("KIWOOM_MODE must be 'mock' or 'live'")

    app = AppCfg(
        name=str(app_y.get("name", "KiWoom")),
        log_dir=str(log_dir()),
    )
    trade = TradeCfg(
        max_orders_per_day=int(trd_y.get("max_orders_per_day", 50)),
        max_daily_loss_pct=float(trd_y.get("max_daily_loss_pct", 3.0)),
    )
    api = ApiCfg(
        mode=mode,
        appkey=_pick_mode_val(mode, "KIWOOM_APPKEY"),
        secret=_pick_mode_val(mode, "KIWOOM_SECRET"),
        acc_no=_pick_mode_val(mode, "ACC_NO"),
        base_url=_base_url(mode),
    )
    cfg = Cfg(app=app, trade=trade, api=api)
    validate_cfg(cfg)
    return cfg


def validate_cfg(cfg: Cfg) -> None:
    """Ensure mode matches API base URL (mock/live separation)."""
    expected = _base_url(cfg.api.mode)
    if cfg.api.base_url.rstrip("/") != expected.rstrip("/"):
        raise ValueError(
            f"KIWOOM_MODE={cfg.api.mode} but base_url={cfg.api.base_url} "
            f"(expected {expected})"
        )
    if not cfg.api.appkey or not cfg.api.secret:
        raise ValueError(f"API keys missing for mode={cfg.api.mode}")
