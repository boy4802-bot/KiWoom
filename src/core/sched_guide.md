# sched.py 해설서

## 하는 일

**한국 거래소(KRX) 장 시간**을 판별합니다. 엔진이 장외에 주문하지 않도록 합니다.

## 함수

| 함수 | 설명 |
|------|------|
| `is_market_open()` | 평일 09:00~15:30 KST 이면 True |
| `market_label()` | `open` / `pre_market` / `after_market` / `weekend` |
| `is_weekday()` | 주말 여부 |

## 검증

```powershell
.\.venv\Scripts\python.exe -c "from src.core.sched import is_market_open, market_label; print(market_label(), is_market_open())"
```

## 참고

점심 단일가·시간외 단일가는 포함하지 않은 **단순 모델**입니다. 필요 시 로드맵에 항목을 추가해 확장합니다.
