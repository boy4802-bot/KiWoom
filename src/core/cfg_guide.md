# cfg.py 해설서

## 이 파일은 무엇을 하나요?

`cfg.py`는 프로그램 설정을 한 곳에서 읽어오는 파일입니다.
`.env`(비밀정보)와 `config/default.yaml`(일반 설정)을 합쳐서 실행에 필요한 값을 만듭니다.

## 어떤 순서로 값을 읽나요?

1. 기본값
2. `config/default.yaml`
3. `.env` (최우선)

즉, `.env`에 적은 값이 있으면 YAML보다 우선합니다.

## 주요 설정

- `KIWOOM_MODE`: `mock` 또는 `live`
- `KIWOOM_APPKEY`: API 앱키
- `KIWOOM_SECRET`: API 시크릿
- `ACC_NO`: 계좌번호
- `trade.max_orders_per_day`: 일일 최대 주문 수
- `trade.max_daily_loss_pct`: 일일 최대 손실률

## 자주 나는 오류

- `KIWOOM_MODE`가 `mock/live`가 아니면 오류가 납니다.
- YAML 문법이 깨졌으면 로드 실패가 납니다.

## 사용 예시

```python
from src.core.cfg import load_cfg

cfg = load_cfg()
print(cfg.api.base_url)
```