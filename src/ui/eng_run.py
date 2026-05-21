"""Background engine runner for Streamlit."""

from __future__ import annotations

import logging
import threading
from typing import Any

from src.core.eng import Engine

log = logging.getLogger("kiwoom")


class EngRunner:
    """Thread-safe wrapper to start/stop Engine.run()."""

    def __init__(self) -> None:
        self._eng: Engine | None = None
        self._thread: threading.Thread | None = None
        self._err: str | None = None
        self._log: list[str] = []

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    @property
    def last_error(self) -> str | None:
        return self._err

    @property
    def messages(self) -> list[str]:
        return list(self._log)

    def bind(self, eng: Engine) -> None:
        self._eng = eng

    def run_once(self) -> list[Any]:
        if self._eng is None:
            return []
        try:
            sigs = self._eng.run_once()
            for s in sigs:
                self._log.append(f"{s.side} {s.stk_cd} qty={s.qty} | {s.why}")
            if len(self._log) > 100:
                self._log = self._log[-100:]
            self._err = None
            return sigs
        except Exception as e:
            self._err = str(e)
            log.exception("engine run_once failed")
            return []

    def start(self) -> None:
        if self._eng is None or self.running:
            return
        self._err = None

        def _target() -> None:
            try:
                assert self._eng is not None
                self._eng.run()
            except Exception as e:
                self._err = str(e)
                log.exception("engine loop failed")

        self._thread = threading.Thread(target=_target, name="kiwoom-eng", daemon=True)
        self._thread.start()
        self._log.append("engine started")

    def stop(self) -> None:
        if self._eng is not None:
            self._eng.stop()
        if self._thread is not None:
            self._thread.join(timeout=5.0)
        self._thread = None
        self._log.append("engine stopped")
