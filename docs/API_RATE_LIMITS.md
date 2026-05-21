# API 호출 제한 메모 (9.3)

## 관측 (모의 mockapi.kiwoom.com)

| 현상 | 대응 |
|------|------|
| HTTP 429 | 연속 REST 호출 시 발생 |
| 모의 ~1 req/s 수준 | 엔진 `interval_sec` ≥ 60 권장 |
| WS 연속 REG | 호출 간 2~3초 |

## 권장 운영

1. 엔진 루프 **60초 이상** 간격
2. `get_prst` 연속 호출 금지 — `ord_dt` 지정, 2~3초 간격
3. WebSocket: `WsPool` 종목 추가·삭제 시 과도한 REG 방지
4. 토큰: `TknMgr` 캐시 사용, 불필요 `issue()` 반복 금지

## 엔진·UI 반영

- `Engine.interval_sec` 기본 60
- `safe.max_orders_per_day` 기본 50 (`config/default.yaml`)
