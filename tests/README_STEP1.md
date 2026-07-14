# Selenium Step 1 적용 방법

압축 파일의 내용을 프로젝트 루트에 덮어씁니다.

## 1. 가상환경 활성화 및 패키지 설치

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2. 환경 파일 생성

`.env.example`을 복사하여 `.env`를 생성합니다.

```powershell
Copy-Item .env.example .env
```

기본 URL은 Vite 개발 서버 설정에 맞춰 아래로 설정되어 있습니다.

```text
http://127.0.0.1:8080
```

## 3. React 앱 실행

첫 번째 터미널:

```powershell
npm install
npm run dev
```

## 4. Smoke Test 실행

두 번째 터미널:

```powershell
.\.venv\Scripts\Activate.ps1
pytest tests/ui/test_smoke.py
```

## 5. Headless 실행

`.env`에서 아래 값을 변경합니다.

```text
HEADLESS=true
```

## 결과물

- HTML 리포트: `reports/test-report.html`
- 실패 스크린샷: `screenshots/`
