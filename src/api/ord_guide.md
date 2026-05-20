# ord.py 해설서

## 이 파일은 무엇을 하나요?

`ord.py`는 주문 API 모듈입니다.
아래 4개 주문 함수를 제공합니다.

## 핵심 함수

- `OrdApi.buy(stk_cd, qty, ...)`
  - 종목코드와 수량으로 매수주문 실행
  - 기본 매매구분은 `3`(시장가)
  - 성공 시 주문번호(`ord_no`) 반환
- `OrdApi.sell(stk_cd, qty, ...)`
  - 매도주문 (`kt10001`)
- `OrdApi.mdfy(orig_ord_no, stk_cd, qty, mdfy_uv, ...)`
  - 정정주문 (`kt10002`)
- `OrdApi.cncl(orig_ord_no, stk_cd, qty=0, ...)`
  - 취소주문 (`kt10003`)
  - `qty=0`이면 잔량 전체 취소
- `OrdApi.get_prst(...)`
  - 계좌별 주문/체결 현황 조회 (`kt00009`)
  - `qry_tp='0'` 전체, `qry_tp='1'` 체결만 조회

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

정정/취소 예시:

```python
md = ord.mdfy(orig_ord_no='0000139', stk_cd='005930', qty=1, mdfy_uv='70000')
cc = ord.cncl(orig_ord_no='0000139', stk_cd='005930', qty=0)
print(md.ord_no, cc.ord_no)
```

주문/체결 현황 조회 예시:

```python
rows = ord.get_prst(qry_tp='0', dmst_stex_tp='KRX')
for r in rows[:3]:
    print(r.ord_no, r.stk_cd, r.cntr_qty, r.acpt_tp)
```

## 주의사항

- 실거래 모드에서는 실제 주문이 체결될 수 있습니다.
- 검증 시 소수량/모의환경으로 먼저 테스트하세요.