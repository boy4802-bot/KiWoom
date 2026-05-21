# 주문 API 장중 검증 (3.1 · 3.2)

> 구현·통합 커밋은 완료. **2026-05-21** 모의 장중 검증 완료 (아래 명령은 재검증·회귀용).

## 검증 결과 (2026-05-21)

| 항목 | 결과 | 비고 |
|------|------|------|
| 3.1 매수 시장가 | OK | ord_no `0031469` |
| 3.2 매도 시장가 | OK | ord_no `0031618` |
| 3.2 정정 | OK | 지정가 250000→251000, mdfy ord `0032417` |
| 3.2 취소 | OK | 지정가 240000 주문 cncl `0032596` |
| kt00009 조회 | OK | `ord_dt=YYYYMMDD` 필요 (빈 값 시 0건) |

> 정정 후 취소는 **원주문번호**가 아닌 정정 응답 `ord_no` 또는 미체결 잔량 기준으로 호출해야 함 (RC4033 참고).

---

> 아래는 **장중(09:00~15:30)** 모의투자에서 실행할 체크리스트입니다.

## 사전 준비

- `.env`에 `KIWOOM_MODE=mock` 및 모의 키·계좌 설정
- venv 활성화 후 프로젝트 루트에서 실행

## 3.1 매수 (kt10000)

```powershell
.\.venv\Scripts\python.exe -c "
from src.core.cfg import load_cfg
from src.api.cli import ApiCli
from src.api.auth import Auth, TknMgr
from src.api.ord import OrdApi

cfg = load_cfg(force_mode='mock')
ord = OrdApi(ApiCli(cfg), TknMgr(Auth(cfg)))
res = ord.buy('005930', 1)
print('BUY_OK', res.ord_no)
"
```

- 성공: `BUY_OK` + 주문번호
- 실패 RC4058: 장 종료 — 장중에 재실행

## 3.2 매도 · 정정 · 취소

1. 위 매수로 받은 `ord_no`를 `orig_ord_no`로 사용 (미체결 시 정정/취소, 체결 후에는 매도 테스트)
2. 매도 1주:

```powershell
.\.venv\Scripts\python.exe -c "
from src.core.cfg import load_cfg
from src.api.cli import ApiCli
from src.api.auth import Auth, TknMgr
from src.api.ord import OrdApi

cfg = load_cfg(force_mode='mock')
ord = OrdApi(ApiCli(cfg), TknMgr(Auth(cfg)))
res = ord.sell('005930', 1)
print('SELL_OK', res.ord_no)
"
```

3. 미체결 주문이 있으면 `mdfy` / `cncl` 각 1회 (유효 `orig_ord_no` 필요)
4. `get_prst()`로 주문·체결 반영 확인

## 완료 후

- `roadmap.md` 3.1·3.2 검증 열에 결과 날짜 기록
- `[3.1-3.2] 모의 장중 주문 검증` 커밋 (선택)

## 참고

- `OrdIdem.buy_once(sig, ...)` 중복 방지는 3.4에서 단위 검증 완료
- 실거래 검증은 별도 승인 후 `force_mode='live'`로만 진행