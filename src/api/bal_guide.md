# bal.py 해설서

## 이 파일은 무엇을 하나요?

`bal.py`는 일별 잔고/수익률을 조회하는 모듈입니다.
키움 API `ka01690`을 호출해서 계좌 전체 평가정보와 종목별 상세 내역을 가져옵니다.

## 핵심 함수

- `BalApi.get_day(qry_dt)`
  - 입력: 조회일자 (`YYYYMMDD`, 생략 시 오늘)
  - 출력: `BalRes` (요약 + 종목 리스트)

## 반환 데이터

- 계좌 요약: 총매입, 총평가, 총손익, 수익률, 예수금
- 종목 목록: 종목코드, 종목명, 보유수량, 매입단가, 현재가, 평가손익

## 사용 예시

```python
from src.core.cfg import load_cfg
from src.api.cli import ApiCli
from src.api.auth import Auth, TknMgr
from src.api.bal import BalApi

cfg = load_cfg()
cli = ApiCli(cfg)
tm = TknMgr(Auth(cfg, cli=cli))
bal = BalApi(cli, tm)
res = bal.get_day('20260520')
print(res.tot_evlt_amt, len(res.items))
```

## 주의사항

문서 기준으로 `ka01690`은 **모의투자 미지원**으로 안내되어 있습니다.
모의 모드에서 오류가 나면 실거래 모드에서 다시 검증해야 합니다.