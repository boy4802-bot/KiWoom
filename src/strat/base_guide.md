# base.py 해설서

## 이 파일은 무엇을 하나요?

전략 **프레임워크의 공통 타입**입니다. 모든 매매 전략은 여기 정의된 `StratBase`를 상속합니다.

## 핵심 타입

| 이름 | 설명 |
|------|------|
| `Sig` | 매수/매도 신호 (주문 API는 호출하지 않음) |
| `Ctx` | 모드(mock/live), 보유수량, 전략 파라미터 |
| `StratBase` | `on_init`, `on_bar` 메서드 |

## Sig.id 중요

`OrdIdem.buy_once(sig.id, ...)` 에 쓰입니다. 같은 id면 주문이 한 번만 나갑니다.

예: `ma_005930_20260521_buy`

## 전략 작성 예시

```python
from src.strat.base import StratBase, Sig, Ctx

class StratMa(StratBase):
    name = "strat_ma"

    def on_bar(self, bars, ctx):
        # ... 판단 ...
        return Sig(id="...", side="buy", stk_cd="005930", qty=1, why="MA cross")
```

## 설계 문서

전체 구조: [docs/STRATEGY_ENGINE.md](../../docs/STRATEGY_ENGINE.md)
