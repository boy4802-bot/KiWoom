# 모의투자 E2E 시나리오 (9.1)

> `KIWOOM_MODE=mock` · 장중 권장

## 사전

- [ ] `Documents\KiWoom\.env` 또는 프로젝트 `.env` 설정
- [ ] venv + `pip install -r requirements.txt`

## 체크리스트

| # | 단계 | 명령/동작 | 기대 |
|---|------|-----------|------|
| 1 | 인증 | `Auth(load_cfg()).issue()` | token 발급 |
| 2 | 시세 | `BarApi.get('005930')` | 봉 수신 |
| 3 | WS | `smoke_cntr()` | 0B 틱 > 0 |
| 4 | 주문 | `VERIFY_ORD_MARKET.md` | BUY/SELL OK |
| 5 | 전략 | `signal_offline('strat_ma')` | Sig 또는 None |
| 6 | 엔진 | `smoke_engine_once(dry_run=True)` | 신호 로그 |
| 7 | UI | `streamlit run app.py` | 탭·설정·차트 |
| 8 | 안전 | 장외 `is_market_open()` False | 주문 스킵 |

## 회귀

- [ ] `load_strat('strat_ma')` / `load_strat('strat_rsi')` 교체
- [ ] `OrdIdem` 동일 sig 2회 → dup

## 기록

| 날짜 | 결과 | 비고 |
|------|------|------|
| 2026-05-21 | 1~7 단위 검증 완료 | 장중 주문 2026-05-21 |
