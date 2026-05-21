# 매매 전략 엔진 설계 (5단계)

> KiWoom 로드맵 5.1~5.6 구현 기준 문서. 단계 완료 시 `roadmap.md`와 함께 갱신합니다.

## 1. 한 줄 요약

| 레이어 | 역할 | 하지 않는 일 |
|--------|------|----------------|
| **전략** (`strategies/*.py`) | 봉/시세를 보고 **매수·매도 신호**만 생성 | REST 주문, 토큰, WebSocket 직접 호출 |
| **엔진** (`src/core/eng.py`) | 주기 루프, 잔고 반영, 신호 → 주문 실행 | 골든크로스 등 매매 규칙 |
| **실행** (`ord.py`, `ord_idem.py`) | 키움 API 주문·중복 방지 | 전략 판단 |

전략 파일을 `strategies/`에 추가만 하면 교체되게 하는 것이 5단계의 핵심 목표입니다.

## 2. 폴더 구조

```
KiWoom/
├── strategies/              # 플러그인 전략 (사용자·샘플)
│   ├── strat_ma.py
│   ├── strat_rsi.py
│   └── *_guide.md
├── src/
│   ├── strat/               # 프레임워크
│   │   ├── base.py          # Sig, Ctx, StratBase
│   │   └── loader.py        # load_strat()
│   └── core/
│       └── eng.py           # Engine 루프
```

## 3. 핵심 모델

### Sig (신호)

- `id`: `OrdIdem.buy_once(sig, ...)` 중복 방지 키 (전략·종목·봉·방향 포함)
- `side`: `buy` | `sell`
- `stk_cd`, `qty`, `why`

### Ctx (전략 컨텍스트)

- `mode`: mock | live
- `positions`: 종목코드 → 보유수량 (`bal`에서 갱신)
- `params`: UI/설정 파라미터 (RSI 기간 등)

### StratBase

- `on_init(ctx)`: 1회 초기화
- `on_bar(bars, ctx) -> Sig | None`: 봉 단위 판단 (5단계 1차 구현)

5단계 1차는 **봉(bar) REST 폴링**. WebSocket `0B` 틱 전략은 5.x 이후 `on_tick` 확장.

## 4. 엔진 루프 (5.5)

```
while running:
    잔고 조회 → ctx.positions 갱신
    watchlist 각 종목:
        bars = BarApi.get(stk_cd)
        sig = strat.on_bar(bars, ctx)
        if sig: OrdIdem.buy_once / sell_once
    sleep(interval_sec)   # 기본 60초, 모의 rate limit 고려
```

검증: 모의·1종목·1주·장중 1회 매매 + `OrdIdem` 중복 차단.

## 5. 로드맵 매핑

| ID | 산출물 | 완료 기준 |
|----|--------|-----------|
| 5.1 | `base.py` | 더미 전략 `on_bar` → Sig |
| 5.2 | `loader.py` | `load_strat("strat_ma")` |
| 5.3 | `strat_ma.py` | 모의 봉으로 신호 로그 (주문 없이) |
| 5.4 | `strat_rsi.py` | params 변경 시 신호 변화 |
| 5.5 | `eng.py` | 모의 자동 1회 매매 |
| 5.6 | Git | MA ↔ RSI 교체 |

## 6. 5단계에서 하지 않을 것

- Streamlit 제어 (6단계)
- 장시간·킬스위치 (7단계 `sched`, `safe`)
- 백테스트·다종목 포트폴리오 (이후)

## 7. 주의사항

1. **동일 봉 중복 신호**: 마지막 처리 `bar.date` 기억
2. **REST 429**: 1종목·60초 주기 권장 (모의 1req/s)
3. **매도 수량**: `min(sig.qty, 보유수량)` 클램프
4. **실거래**: 5.x는 mock만

## 8. 6·7단계 연동

- 6단계: Streamlit이 `Engine` start/stop, `params` 편집
- 7단계: `safe.can_trade()`가 엔진 앞에서 차단 (전략 수정 불필요)
