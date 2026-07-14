# Pa-Bi Auction QA Automation Portfolio

Python, Selenium, pytest를 기반으로 Pa-Bi Auction 서비스의 UI 및 API를 검증하는 QA 자동화 프로젝트입니다.

## 기술 구성

- Python
- Selenium
- pytest
- requests
- pytest-html
- python-dotenv
- GitHub Actions

## 프로젝트 구조

```text
pa-bi-auction-selenium-qa/
├── docs/
├── tests/
│   ├── ui/
│   ├── api/
│   ├── pages/
│   ├── data/
│   ├── utils/
│   └── conftest.py
├── reports/
├── screenshots/
├── .github/workflows/
├── .env.example
├── .gitignore
├── pytest.ini
└── requirements.txt
```

## 초기 실행 준비

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

패키지 설치:

```bash
pip install -r requirements.txt
```

테스트 실행:

```bash
pytest
```

현재 파일은 기본 구조만 포함합니다. 실제 URL, 화면 요소, 테스트 계정 및 테스트 로직은 이후 단계에서 구현합니다.
