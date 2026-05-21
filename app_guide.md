# app.py 해설서

## 이 파일은 무엇을 하나요?

KiWoom **메인 화면**(Streamlit)입니다. 로드맵 6단계 UI입니다.

| 탭 | 기능 |
|----|------|
| 대시보드 | 모드·계좌·잔고 조회 |
| 차트 | 종목 봉 차트 |
| 전략 | 전략 선택, 1회/연속 실행, 중지 |
| 주문·체결 | 당일 주문/체결 테이블 |

## 실행

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```

브라우저: `http://localhost:8501`

## 사이드바 (API 설정)

- 모의/실거래 모드 선택
- 앱키·시크릿·계좌번호 입력 후 **설정 저장** → `.env` 갱신
- 비밀값은 Git에 올리지 마세요

## 전략 탭

- `strategies/` 에 있는 전략 목록에서 선택
- **드라이런**: 체크 시 주문 없이 신호만 (권장)
- **연속 시작**: 백그라운드에서 엔진 루프 (`eng.py`)
- **중지**: 루프 종료

## 관련 모듈

- `src/ui/env_io.py` — .env 읽기/쓰기
- `src/ui/eng_run.py` — 엔진 백그라운드 실행
- [docs/STRATEGY_ENGINE.md](docs/STRATEGY_ENGINE.md)
