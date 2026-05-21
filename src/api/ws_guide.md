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

## 4.2 체결(0B) 콜백

`reg()`로 등록하고 `on_cntr` 콜백으로 체결 틱을 받습니다.

```python
from src.api.ws import WsCli, RtCntr

def on_tick(c: RtCntr):
    print(c.item, c.tm, c.cur_prc, c.cntr_qty)

ws = WsCli(cfg, TknMgr(Auth(cfg)), on_cntr=on_tick)
await ws.connect()
await ws.reg(['005930'], ['0B'])
```

검증: `asyncio.run(smoke_cntr())` — 장중에 0보다 큰 틱 수가 나오면 OK.

## 4.3 호가(0D) · 잔고(04) · 주문(00)

| 타입 | 등록 | 콜백 |
|------|------|------|
| `0D` | `reg_stk(['005930'], ['0D'])` | `on_hoga` → `RtHoga` |
| `04` | `reg_acc(['04'])` (계좌번호) | `on_bal` → `RtBal` |
| `00` | `reg_acc(['00'])` | `on_ord` → `RtOrd` |

```python
await ws.reg_stk(['005930'], ['0B', '0D'])
await ws.reg_acc(['04', '00'])  # .env ACC_NO 필요
```

- `0D`는 장중 종목 호가 변경 시 수신됩니다.
- `04`/`00`은 **잔고·주문 변동**이 있을 때만 이벤트가 옵니다(REG 성공 ≠ 즉시 수신).

검증: `asyncio.run(smoke_rt())` → `0B`·`0D` > 0 (장중).

## 주의사항

- REST OAuth 토큰(`TknMgr`)이 있어야 `LOGIN`이 성공합니다.
- 모의 WebSocket은 KRX 위주입니다.
- `run()`은 백그라운드 태스크로 실행하고, UI/엔진 종료 시 `close()`를 호출하세요.
