# qte.py 해설서

## 이 파일은 무엇을 하나요?

`qte.py`는 시세 조회 모듈입니다.
- `ka10003`: 체결정보
- `ka10004`: 호가정보

## 핵심 함수

- `QteApi.get_cntr(stk_cd)`
  - 최근 체결 리스트 반환
- `QteApi.get_hoga(stk_cd)`
  - 1호가(매도/매수)와 수량, 호가시간 반환

## 반환 데이터

- `Cntr`: 시간, 현재가, 전일대비, 등락률, 체결거래량 등
- `Hoga`: 호가시간, 1차 매도/매수호가, 수량, raw 응답

## 사용 예시

```python
from src.core.cfg import load_cfg
from src.api.cli import ApiCli
from src.api.auth import Auth, TknMgr
from src.api.qte import QteApi

cfg = load_cfg()
cli = ApiCli(cfg)
tm = TknMgr(Auth(cfg, cli=cli))
q = QteApi(cli, tm)

cntr = q.get_cntr('005930')
hoga = q.get_hoga('005930')
print(len(cntr), hoga.ask1, hoga.bid1)
```