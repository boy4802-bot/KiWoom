# strat_ma.py 해설서

## 하는 일

단기·장기 **이동평균 교차**로 매수/매도 신호를 냅니다.

- 골든크로스(단기 > 장기): 보유 없을 때 매수
- 데드크로스(단기 < 장기): 보유 있을 때 매도

## 파라미터

| 이름 | 기본 | 설명 |
|------|------|------|
| `short` | 5 | 단기 이평 봉 수 |
| `long` | 20 | 장기 이평 봉 수 |

`Ctx.params`: `stk_cd`, `qty`

## 로드

```python
from src.strat.loader import load_strat
strat = load_strat("strat_ma", short=5, long=20)
```

## 검증 (주문 없이)

```powershell
.\.venv\Scripts\python.exe -c "from src.strat.smoke import signal_once; print(signal_once('strat_ma'))"
```
