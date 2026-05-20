# app.py 해설서

## 이 파일은 무엇을 하나요?

`app.py`는 **KiWoom 자동매매 프로그램의 메인 화면**을 여는 파일입니다.  
Streamlit을 사용해, 웹 브라우저처럼 보이는 창에서 계좌·전략·주문을 확인하고 조작할 수 있습니다.

## 언제 실행하나요?

개발이 어느 정도 진행된 뒤(로드맵 **6단계** 이후), 아래 명령으로 실행합니다.

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```

실행하면 브라우저가 열리고 `http://localhost:8501` 주소로 접속됩니다.

## 사용자가 바꿔도 되는 것

- 나중에 추가될 **전략 선택**, **매수·매도 수량**, **모의/실거래 전환** 등은 화면에서 설정합니다.
- API 키는 `.env` 파일에 저장합니다 (화면 입력 기능은 추후 추가).

## 건드리면 안 되는 것

- `app.py` 안의 Streamlit 기본 설정은 개발자가 수정합니다.
- API 키를 코드 안에 직접 적지 마세요.

## 자주 나오는 오류

| 증상 | 해결 |
|------|------|
| `streamlit` 명령을 찾을 수 없음 | 가상환경 활성화 후 `pip install -r requirements.txt` |
| 브라우저가 안 열림 | 터미널에 표시된 URL을 직접 복사해 접속 |
| API 오류 | `.env`의 앱키·시크릿 확인, 모의투자 모드 확인 |

## 관련 문서

- [roadmap.md](roadmap.md) — 전체 개발 순서
- [docs/DEVELOPMENT_PRINCIPLES.md](docs/DEVELOPMENT_PRINCIPLES.md) — 개발 원칙