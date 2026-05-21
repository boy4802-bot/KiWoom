# ws.py 해설서

## 이 파일은 무엇을 하나요?

`ws.py`는 키움 REST API **실시간 WebSocket** 클라이언트입니다.
로드맵 4.1 단계에서 연결·로그인·PING 응답·재연결을 담당합니다.

## 접속 주소

| 모드 | URL |
|------|-----|
| mock | `wss://mockapi.kiwoom.com:10000/api/dostk/websocket` |
| live | `wss://api.kiwoom.com:10000/api/dostk/websocket` |

`ws_url(cfg)` 함수가 `KIWOOM_MODE`에 맞는 주소를 만듭니다.

## 핵심 클래스: `WsCli`

- `connect()` — 서버 연결 후 `LOGIN` 패킷 전송·성공 확인
- `send(msg)` — JSON 메시지 전송 (`REG` 등은 4.2~4.4에서 사용)
- `run()` — 수신 루프 + 끊김 시 자동 재연결
- `close()` — 연결 종료

서버가 보내는 `PING`은 수신 내용을 그대로 다시 보냅니다(키움 가이드 동일).

## 사용 예시 (연결 확인)

```python
import asyncio
from src.core.cfg import load_cfg
from src.api.auth import Auth, TknMgr
from src.api.ws import WsCli, smoke_login

async def main():
    cfg = load_cfg(force_mode='mock')
    ws = WsCli(cfg, TknMgr(Auth(cfg)))
    await ws.connect()
    await asyncio.sleep(2)
    await ws.close()

asyncio.run(main())
# 또는
asyncio.run(smoke_login())
```

## 4.2 이후 (실시간 등록)

체결·호가 등록은 `send()`로 `REG` 메시지를 보냅니다.

```python
await ws.send({
    'trnm': 'REG',
    'grp_no': '1',
    'refresh': '1',
    'data': [{'item': ['005930'], 'type': ['0B']}],
})
```

## 주의사항

- REST OAuth 토큰(`TknMgr`)이 있어야 `LOGIN`이 성공합니다.
- 모의 WebSocket은 KRX 위주입니다.
- `run()`은 백그라운드 태스크로 실행하고, UI/엔진 종료 시 `close()`를 호출하세요.
