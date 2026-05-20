# KiWoom — 키움 REST API 자동매매

키움증권 REST API와 Streamlit을 이용한 **국내주식 자동매매** 프로그램입니다.

## 문서

| 문서 | 설명 |
|------|------|
| [roadmap.md](roadmap.md) | 트리형 개발 로드맵·진행 상황 |
| [docs/DEVELOPMENT_PRINCIPLES.md](docs/DEVELOPMENT_PRINCIPLES.md) | 개발 시 지켜야 할 원칙 |

## 환경 요구사항

- Windows 10/11 **64bit**
- Python **3.11+ 64bit**
- 키움증권 REST API 앱키·시크릿키 ([키움 Open API](https://openapi.kiwoom.com/))
- 키움 REST API 문서는 "D:\Projects\KiWoom\docs\키움 REST API 문서.pdf" 에서 참조할 것것

## 빠른 시작 (개발 중)

```powershell
# 64bit Python 확인
python -c "import struct; print(struct.calcsize('P')*8)"

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# .env 에 appkey, secretkey 입력

streamlit run app.py
```

## API 환경

| 구분 | URL |
|------|-----|
| 운영(실거래) | `https://api.kiwoom.com` |
| 모의투자 | `https://mockapi.kiwoom.com` |

> 실거래 전 반드시 모의투자 환경에서 검증하세요.

## 한글 깨짐 방지

- 모든 문서는 **UTF-8** 로 저장합니다.
- Cursor 우측 하단 인코딩이 `UTF-8` 인지 확인하세요.
- 깨져 보이면: 명령 팔레트 → `Reopen with Encoding` → `UTF-8`

## 라이선스·면책

본 프로그램은 투자 손실에 대한 책임을 지지 않습니다. 자동매매 사용 전 약관·API 이용 정책을 확인하세요.