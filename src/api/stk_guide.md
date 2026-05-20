# stk.py 해설서

## 이 파일은 무엇을 하나요?

`stk.py`는 종목 기본정보를 조회하는 모듈입니다.
키움 API `ka10001`을 호출해 종목명, 현재가, 등락률, 거래량 같은 핵심 필드를 가져옵니다.

## 핵심 함수

- `StkApi.get_info(stk_cd)`
  - 입력: 종목코드 (예: `005930`)
  - 출력: `StkInfo`

## 반환 항목

- `stk_cd`, `stk_nm`
- `cur_prc` (현재가)
- `pred_pre` (전일대비)
- `flu_rt` (등락률)
- `trde_qty` (거래량)
- `open_pric`, `high_pric`, `low_pric`

## 사용 예시

```python
from src.core.cfg import load_cfg
from src.api.cli import ApiCli
from src.api.auth import Auth, TknMgr
from src.api.stk import StkApi

cfg = load_cfg()
cli = ApiCli(cfg)
tm = TknMgr(Auth(cfg, cli=cli))
api = StkApi(cli, tm)
info = api.get_info('005930')
print(info.stk_nm, info.cur_prc, info.flu_rt)
```