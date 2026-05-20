# log.py 해설서

## 이 파일은 무엇을 하나요?

`log.py`는 로그를 콘솔과 파일(`logs/app.log`)에 동시에 남기도록 설정합니다.
문제가 생겼을 때 원인을 추적하기 쉽게 만드는 핵심 모듈입니다.

## 주요 기능

- 콘솔 출력
- 파일 로그 저장
- 로그 파일 크기 초과 시 자동 순환(rotate)

## 파일 회전 설정

- 파일명: `logs/app.log`
- 최대 크기: 5MB
- 백업 파일 수: 5개

## 사용 예시

```python
from src.core.log import init_log

log = init_log('kiwoom')
log.info('logger ready')
```

## 주의

- 같은 logger를 다시 초기화해도 핸들러가 중복되지 않도록 처리되어 있습니다.