# ord_idem.py 해설서

## 이 파일은 무엇을 하나요?

`ord_idem.py`는 **같은 매매 신호가 두 번 들어와도 주문은 한 번만** 나가게 막는 보호 모듈입니다.
전략이 같은 조건을 연속으로 보낼 때 중복 주문을 방지합니다.

## 핵심 개념

- `sig`(신호 ID): 전략이 만드는 고유 문자열 (예: `ma_cross_005930_20260520`)
- 첫 호출: 실제 `buy`/`sell` API 호출
- 두 번째 동일 `sig`: API 호출 없이 첫 결과 재사용 (`dup=True`)

## 핵심 함수

- `OrdIdem.buy_once(sig, stk_cd, qty, ...)`
- `OrdIdem.sell_once(sig, stk_cd, qty, ...)`
- `OrdIdem.has(sig)` — 이미 주문했는지 확인
- `OrdIdem.clear()` — 맵 초기화 (테스트/장 마감 후)

## 사용 예시

```python
from src.core.cfg import load_cfg
from src.api.cli import ApiCli
from src.api.auth import Auth, TknMgr
from src.api.ord import OrdApi
from src.api.ord_idem import OrdIdem

cfg = load_cfg()
guard = OrdIdem(OrdApi(ApiCli(cfg), TknMgr(Auth(cfg))))

r1 = guard.buy_once('sig-001', '005930', 1)
r2 = guard.buy_once('sig-001', '005930', 1)
print(r1.dup, r2.dup)  # False True
```

## 주의사항

- `sig`는 전략·종목·방향·봉시각 등을 조합해 **충돌 없이** 설계하세요.
- 장이 끝난 뒤 다음 날에는 새 `sig`를 쓰거나 `clear()`로 초기화하세요.