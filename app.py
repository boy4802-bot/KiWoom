"""KiWoom Streamlit UI — dashboard, chart, strategy, orders."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.api.auth import Auth, TknMgr
from src.api.bal import BalApi
from src.api.bar import BarApi
from src.api.cli import ApiCli
from src.api.ord import OrdApi
from src.core.cfg import load_cfg
from src.core.sched import is_market_open, market_label
from src.core.state import load_state
from src.core.eng import make_engine
from src.strat.loader import list_strats
from src.ui.eng_run import EngRunner
from src.core.paths import env_file, install_root
from src.ui.env_io import load_env_file, save_env_file

ROOT = install_root()


def _init_state() -> None:
    if "runner" not in st.session_state:
        st.session_state.runner = EngRunner()
    if "ui_log" not in st.session_state:
        st.session_state.ui_log: list[str] = []


def _api_clients():
    load_dotenv(env_file(), override=True)
    cfg = load_cfg()
    cli = ApiCli(cfg)
    tm = TknMgr(Auth(cfg, cli=cli))
    return cfg, cli, tm


def _ui_log(msg: str) -> None:
    st.session_state.ui_log.append(f"{datetime.now():%H:%M:%S} {msg}")
    if len(st.session_state.ui_log) > 200:
        st.session_state.ui_log = st.session_state.ui_log[-200:]


def _sidebar_settings() -> None:
    st.sidebar.header("API 설정")
    env = load_env_file()
    mode = st.sidebar.selectbox(
        "거래 모드",
        ["mock", "live"],
        index=0 if env.get("KIWOOM_MODE", "mock") != "live" else 1,
    )
    st.sidebar.caption("mock=모의투자, live=실거래 (주의)")

    with st.sidebar.expander("모의투자 키", expanded=mode == "mock"):
        mock_key = st.text_input("APPKEY (모의)", env.get("KIWOOM_APPKEY_MOCK", ""), type="default")
        mock_sec = st.text_input("SECRET (모의)", env.get("KIWOOM_SECRET_MOCK", ""), type="password")
        mock_acc = st.text_input("계좌번호 (모의)", env.get("ACC_NO_MOCK", ""))

    with st.sidebar.expander("실거래 키", expanded=mode == "live"):
        live_key = st.text_input("APPKEY (실)", env.get("KIWOOM_APPKEY_LIVE", ""))
        live_sec = st.text_input("SECRET (실)", env.get("KIWOOM_SECRET_LIVE", ""), type="password")
        live_acc = st.text_input("계좌번호 (실)", env.get("ACC_NO_LIVE", ""))

    if st.sidebar.button("설정 저장 (.env)", type="primary"):
        save_env_file(
            {
                "KIWOOM_MODE": mode,
                "KIWOOM_APPKEY_MOCK": mock_key,
                "KIWOOM_SECRET_MOCK": mock_sec,
                "ACC_NO_MOCK": mock_acc,
                "KIWOOM_APPKEY_LIVE": live_key,
                "KIWOOM_SECRET_LIVE": live_sec,
                "ACC_NO_LIVE": live_acc,
            }
        )
        load_dotenv(env_file(), override=True)
        _ui_log(f"설정 저장 완료 (mode={mode})")
        st.sidebar.success("저장했습니다. 탭을 새로고침하세요.")
        st.rerun()

    st.sidebar.divider()
    st.sidebar.markdown("**로그**")
    for line in reversed(st.session_state.ui_log[-8:]):
        st.sidebar.caption(line)


def _tab_dashboard() -> None:
    st.subheader("대시보드")
    cfg, cli, tm = _api_clients()
    c1, c2, c3 = st.columns(3)
    c1.metric("모드", cfg.api.mode)
    c2.metric("계좌", cfg.api.acc_no or "(미설정)")
    c3.metric("엔진", "실행 중" if st.session_state.runner.running else "정지")
    mlabel = market_label()
    st.caption(
        f"장 상태: **{mlabel}** ({'주문 가능' if is_market_open() else '장외 — 주문 차단'}) · "
        f"오늘 주문 {load_state().order_count}건"
    )

    if st.button("잔고 새로고침"):
        try:
            bal = BalApi(cli, tm).get_day()
            st.success(f"조회일 {bal.dt}")
            if bal.items:
                df = pd.DataFrame(
                    [
                        {
                            "종목": f"{it.stk_nm} ({it.stk_cd})",
                            "수량": it.rmnd_qty,
                            "현재가": it.cur_prc,
                            "평가손익": it.evltv_prft,
                            "수익률%": it.prft_rt,
                        }
                        for it in bal.items
                    ]
                )
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("보유 종목이 없거나 데이터가 비어 있습니다.")
            _ui_log("잔고 조회 OK")
        except Exception as e:
            st.warning(f"잔고 조회 실패: {e}")
            st.caption("모의 환경에서는 일부 잔고 API가 지원되지 않을 수 있습니다.")
            _ui_log(f"잔고 오류: {e}")


def _tab_chart() -> None:
    st.subheader("차트")
    stk = st.text_input("종목코드", "005930", key="chart_stk")
    n = st.slider("봉 개수", 10, 120, 60, key="chart_n")
    if st.button("차트 불러오기", key="chart_load"):
        try:
            _, cli, tm = _api_clients()
            bars = BarApi(cli, tm).get(stk, n)
            df = BarApi(cli, tm).to_df(bars)
            if df.empty:
                st.warning("봉 데이터가 없습니다.")
                return
            st.line_chart(df.set_index("date")["close"], height=400)
            st.dataframe(df.tail(10), use_container_width=True, hide_index=True)
            _ui_log(f"차트 {stk} {len(df)}봉")
        except Exception as e:
            st.error(str(e))
            _ui_log(f"차트 오류: {e}")


def _tab_strategy() -> None:
    st.subheader("전략 · 엔진")
    strats = [s for s in list_strats() if s != "strat_dummy"]
    if not strats:
        strats = list_strats()
    strat_name = st.selectbox("전략", strats, index=0)
    stk = st.text_input("감시 종목", "005930", key="strat_stk")
    interval = st.slider("루프 간격(초)", 30, 300, 60, key="strat_iv")
    dry = st.checkbox("드라이런 (주문 안 함)", value=True)

    runner: EngRunner = st.session_state.runner
    st.caption(f"상태: {'실행 중' if runner.running else '정지'}")
    if runner.last_error:
        st.error(runner.last_error)

    c1, c2, c3 = st.columns(3)
    if c1.button("1회 실행"):
        try:
            load_dotenv(env_file(), override=True)
            eng = make_engine(
                strat_name,
                [stk.strip()],
                dry_run=dry,
                strat_params={"stk_cd": stk.strip(), "qty": 1},
            )
            runner.bind(eng)
            sigs = runner.run_once()
            _ui_log(f"1회 실행 sigs={len(sigs)} dry={dry}")
            st.success(f"신호 {len(sigs)}건")
            for s in sigs:
                st.write(f"- {s.side} {s.stk_cd} qty={s.qty} | {s.why}")
        except Exception as e:
            st.error(str(e))

    if c2.button("연속 시작"):
        try:
            load_dotenv(env_file(), override=True)
            eng = make_engine(
                strat_name,
                [stk.strip()],
                interval_sec=float(interval),
                dry_run=dry,
                strat_params={"stk_cd": stk.strip(), "qty": 1},
            )
            runner.bind(eng)
            runner.start()
            _ui_log(f"연속 시작 {strat_name}")
            st.rerun()
        except Exception as e:
            st.error(str(e))

    if c3.button("중지"):
        runner.stop()
        _ui_log("엔진 중지")
        st.rerun()

    st.markdown("**엔진 로그**")
    for line in reversed(runner.messages[-15:]):
        st.text(line)


def _tab_orders() -> None:
    st.subheader("주문 · 체결")
    today = datetime.now().strftime("%Y%m%d")
    if st.button("오늘 주문/체결 조회"):
        try:
            _, cli, tm = _api_clients()
            rows = OrdApi(cli, tm).get_prst(ord_dt=today, qry_tp="0")
            if not rows:
                st.info("내역이 없습니다. ord_dt 또는 장중 여부를 확인하세요.")
                return
            df = pd.DataFrame(
                [
                    {
                        "주문번호": r.ord_no,
                        "종목": r.stk_cd,
                        "구분": r.io_tp_nm,
                        "주문수량": r.ord_qty,
                        "체결수량": r.cntr_qty,
                        "상태": r.acpt_tp,
                    }
                    for r in rows
                ]
            )
            st.dataframe(df, use_container_width=True, hide_index=True)
            _ui_log(f"주문조회 {len(df)}건")
        except Exception as e:
            st.error(str(e))
            _ui_log(f"주문조회 오류: {e}")


def main() -> None:
    st.set_page_config(page_title="KiWoom", layout="wide")
    _init_state()
    st.title("KiWoom 자동매매")
    st.caption("모의투자 검증 후 실거래를 사용하세요. 전략은 strategies/ 폴더에서 교체할 수 있습니다.")

    _sidebar_settings()

    t1, t2, t3, t4 = st.tabs(["대시보드", "차트", "전략", "주문·체결"])
    with t1:
        _tab_dashboard()
    with t2:
        _tab_chart()
    with t3:
        _tab_strategy()
    with t4:
        _tab_orders()


if __name__ == "__main__":
    main()
