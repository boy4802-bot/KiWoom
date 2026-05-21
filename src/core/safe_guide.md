# safe.py 해설서

## 하는 일

**킬 스위치** — 하루 주문 횟수·평가 손실 한도를 넘으면 추가 주문을 막습니다.

설정: `config/default.yaml` 의 `trade.max_orders_per_day`, `trade.max_daily_loss_pct`

## 사용

```python
from src.core.cfg import load_cfg
from src.core.safe import Safe

safe = Safe(load_cfg())
v = safe.can_trade(cur_evlt_amt=1_000_000)
if v.ok:
    # 주문 가능
```

주문 성공 후 `safe.record_order()` 호출 (엔진이 자동 처리).

## 상태 파일

`data/eng_state.json` — 일별 주문 횟수·시작 평가금액 저장 (7.4 장애 복구와 공유)
