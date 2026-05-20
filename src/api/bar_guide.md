# bar.py 해설서

## 이 파일은 무엇을 하나요?

`bar.py`는 봉 데이터(OHLCV)를 조회하는 모듈입니다.
키움 API `ka10005`를 호출해 종목의 시가/고가/저가/종가/거래량 데이터를 가져옵니다.

## 핵심 함수

- `BarApi.get(stk_cd, n)`
  - 종목코드 기준으로 최대 `n`개 봉 데이터를 반환
- `BarApi.to_df(bars)`
  - 봉 리스트를 판다스 DataFrame으로 변환

## DataFrame 컬럼

- `date`, `open`, `high`, `low`, `close`, `volume`, `amount`

## 사용 예시

```python
from src.core.cfg import load_cfg
from src.api.cli import ApiCli
from src.api.auth import Auth, TknMgr
from src.api.bar import BarApi

cfg = load_cfg()
cli = ApiCli(cfg)
tm = TknMgr(Auth(cfg, cli=cli))
bar = BarApi(cli, tm)
rows = bar.get('005930', n=30)
df = bar.to_df(rows)
print(df.tail())
```