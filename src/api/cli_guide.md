# cli.py 해설서

## 이 파일은 무엇을 하나요?

`cli.py`는 키움 REST API를 호출하기 위한 공통 클라이언트입니다.
모든 API 모듈(`auth.py`, `acc.py`, `ord.py` 등)은 이 클라이언트를 통해 요청하도록 만들면 중복 코드가 줄어듭니다.

## 핵심 기능

- `mk_hdr(...)`: 키움 API 형식에 맞는 헤더 생성
- `req(...)`: 공통 HTTP 요청 실행 + 응답 파싱
- `ping()`: 베이스 도메인 연결 상태 확인

## 왜 필요한가요?

각 API마다 매번 URL/헤더/예외 처리 코드를 쓰면 실수가 늘어납니다.
공통 클라이언트를 먼저 만들면 인증/주문/시세 모듈을 빠르게 확장할 수 있습니다.

## 사용 예시

```python
from src.core.cfg import load_cfg
from src.api.cli import ApiCli

cfg = load_cfg()
cli = ApiCli(cfg)
ok, status = cli.ping()
print(ok, status)
```

## 주의사항

- `req()`는 HTTP 상태코드가 4xx/5xx면 예외를 발생시킵니다.
- 실제 업무에서는 `return_code`가 0이 아닌 경우도 별도 처리해야 합니다(1.4 단계).