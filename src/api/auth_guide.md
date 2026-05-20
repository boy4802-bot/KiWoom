# auth.py 해설서

## 이 파일은 무엇을 하나요?

`auth.py`는 키움 REST API OAuth 토큰을 발급하는 모듈입니다.
로드맵 1.2 단계의 핵심으로, 이후 계좌조회/주문 API 호출 전에 반드시 먼저 실행됩니다.

## 핵심 함수

- `Auth.issue()`
  - API ID: `au10001`
  - URL: `/oauth2/token`
  - 요청 바디: `grant_type`, `appkey`, `secretkey`
  - 성공 시 토큰, 타입, 만료시간을 `Tkn` 객체로 반환

## 실행 전 준비

1. `.env` 파일에 아래 값을 넣어야 합니다.
   - `KIWOOM_APPKEY`
   - `KIWOOM_SECRET`
   - `KIWOOM_MODE` (`mock` 권장)
2. 모의투자/실거래 도메인은 `cfg.py`가 자동 선택합니다.

## 사용 예시

```python
from src.core.cfg import load_cfg
from src.api.auth import Auth

cfg = load_cfg()
auth = Auth(cfg)
t = auth.issue()
print(t.typ, t.val[:10], t.exp_dt)
```

## 자주 나는 오류

- 앱키/시크릿 오입력: `return_code != 0`
- 네트워크 오류: HTTP 예외
- 빈 토큰: 응답 파싱 실패 또는 인증 실패