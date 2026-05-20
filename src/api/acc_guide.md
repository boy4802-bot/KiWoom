# acc.py 해설서

## 이 파일은 무엇을 하나요?

`acc.py`는 계좌번호를 조회하는 API 모듈입니다.
키움 문서의 `ka00001`을 사용하며, 현재 토큰 기준으로 사용 가능한 계좌번호를 가져옵니다.

## 핵심 클래스

- `AccApi`
  - `get_acc_no()`: 계좌번호 1건 조회

## 내부 동작

1. `TknMgr`에서 유효 토큰 확보
2. `POST /api/dostk/acnt` 호출 (`api-id: ka00001`)
3. `return_code` 검사
4. `acctNo`를 `AccRes`로 반환

## 사용 예시

```python
from src.core.cfg import load_cfg
from src.api.cli import ApiCli
from src.api.auth import Auth, TknMgr
from src.api.acc import AccApi

cfg = load_cfg()
cli = ApiCli(cfg)
tm = TknMgr(Auth(cfg, cli=cli))
acc = AccApi(cli, tm)
res = acc.get_acc_no()
print(res.acc_no)
```

## 주의사항

- 모의/실거래는 `.env`의 `KIWOOM_MODE`에 따라 자동 결정됩니다.
- 토큰 만료 시 `TknMgr`가 자동 재발급을 시도합니다.