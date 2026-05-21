# loader.py 해설서

## 이 파일은 무엇을 하나요?

`strategies/` 폴더 안의 전략 파일을 **이름만으로 불러옵니다**.

## 사용 예시

```python
from src.strat.loader import load_strat, list_strats

print(list_strats())  # ['strat_dummy', 'strat_ma', ...]
ma = load_strat("strat_ma", short=5, long=20)
```

## 규칙

- 파일명: `strat_*.py` (예: `strat_ma.py`)
- 파일 안에 `StratBase`를 상속한 클래스 **정확히 1개**
- 엔진·UI는 `load_strat("strat_ma")` 만 호출

## 자주 나는 오류

- 클래스가 0개 또는 2개 이상 → `ValueError`
- 파일 없음 → `FileNotFoundError`
