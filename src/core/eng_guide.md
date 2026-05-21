# eng.py 해설서

## 이 파일은 무엇을 하나요?

**매매 전략 엔진**입니다. 전략(`StratBase`)이 낸 신호를 받아 잔고를 갱신하고, `OrdIdem`으로 주문합니다.

## 핵심 클래스 `Engine`

| 메서드 | 설명 |
|--------|------|
| `run_once()` | 1회: 봉 조회 → `on_bar` → 주문(또는 dry_run 로그) |
| `run()` | `interval_sec` 간격 반복 (기본 60초) |
| `stop()` | 루프 종료 |

## 빠른 사용

```python
from src.core.eng import make_engine

eng = make_engine("strat_ma", ["005930"], dry_run=True)
eng.run_once()   # 신호·로그만
# eng.run(max_ticks=1)  # 1틱 후 종료
```

## 모의 1회 주문 검증 (5.5, 장중)

```python
from src.core.eng import make_engine
from src.core.cfg import load_cfg

eng = make_engine(
    "strat_dummy",
    ["005930"],
    cfg=load_cfg(force_mode="mock"),
    dry_run=False,
)
eng.run_once()
```

`strat_dummy`는 **한 번만** 매수 신호를 냅니다. 같은 `sig.id`로 다시 호출하면 `OrdIdem`이 중복 주문을 막습니다.

## 설계 문서

[docs/STRATEGY_ENGINE.md](../../docs/STRATEGY_ENGINE.md)
