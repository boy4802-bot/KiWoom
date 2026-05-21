# strat_rsi.py 해설서

## 하는 일

**RSI**가 과매도/과매수 구간일 때 신호를 냅니다.

- RSI ≤ `buy_below` (기본 30): 매수
- RSI ≥ `sell_above` (기본 70): 매도

## 파라미터

생성자: `period`, `buy_below`, `sell_above`

`Ctx.params`로 UI에서 덮어쓸 수 있습니다.

| param | 기본 | 설명 |
|-------|------|------|
| `rsi_period` | 14 | RSI 기간 |
| `rsi_buy_below` | 30 | 매수 임계 |
| `rsi_sell_above` | 70 | 매도 임계 |
| `stk_cd`, `qty` | — | 종목·수량 |

## 로드

```python
strat = load_strat("strat_rsi", period=14, buy_below=30, sell_above=70)
```
