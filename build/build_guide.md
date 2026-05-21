# 배포 빌드 해설서

## 요구사항

- Windows 64bit
- Python 3.11+ 64bit 가상환경
- `pip install pyinstaller`

## 빌드

```powershell
cd D:\Projects\KiWoom
.\.venv\Scripts\Activate.ps1
pyinstaller build/app.spec --noconfirm
```

산출물: `dist/KiWoom/KiWoom.exe`

## 실행

1. `Documents\KiWoom\.env` 에 API 키 설정 (최초 UI 저장 시 자동 생성 가능)
2. `dist\KiWoom\KiWoom.exe` 더블클릭 또는 `KiWoom.bat`
3. 브라우저 `http://localhost:8501`

## 개발 모드 (빌드 없이)

```powershell
streamlit run app.py
```

## 설정 경로 (8.3)

| 항목 | 경로 |
|------|------|
| 사용자 설정 | `%USERPROFILE%\Documents\KiWoom\.env` |
| 상태·데이터 | `Documents\KiWoom\data\` |
| 로그 | `Documents\KiWoom\logs\` |

## 문제 해결

- 백신이 exe 차단 → 예외 등록
- Streamlit 미로딩 → `pyinstaller build/app.spec` 재실행, hiddenimports 확인
