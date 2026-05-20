# ord.py 해설서

## 이 파일은 무엇을 하나요?

`ord.py`는 주문 API 모듈입니다.
현재는 `kt10000`(매수주문)을 구현했으며, 이후 매도/정정/취소 함수가 같은 파일에 확장됩니다.

## 핵심 함수

- `OrdApi.buy(stk_cd, qty, ...)`
  - 종목코드와 수량으로 매수주문 실행
  - 기본 매매구분은 `3`(시장가)
  - 성공 시 주문번호(`ord_no`) 반환

## 주요 인자

- `stk_cd`: 종목코드 (예: `005930`)
- `qty`: 주문수량
- `dmst_stex_tp`: 거래소 구분 (`KRX`, `NXT`, `SOR`)
- `trde_tp`: 매매구분 (기본 `3`, 시장가)
- `ord_uv`: 주문단가 (지정가일 때 사용)

## 사용 예시 (모의)

```python
from src.core.cfg import load_cfg
from src.api.cli import ApiCli
from src.api.auth import Auth, TknMgr
from src.api.ord import OrdApi

cfg = load_cfg(force_mode='mock')
cli = ApiCli(cfg)
tm = TknMgr(Auth(cfg, cli=cli))
ord = OrdApi(cli, tm)
res = ord.buy('005930', 1)
print(res.ord_no)
```

## 주의사항

- 실거래 모드에서는 실제 주문이 체결될 수 있습니다.
- 검증 시 소수량/모의환경으로 먼저 테스트하세요.