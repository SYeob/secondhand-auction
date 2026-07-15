# Pa-Bi Auction QA Automation Portfolio

Pa-Bi Auction의 금전·개인정보 위험을 중심으로 UI와 API를 함께 검증하는 QA 자동화 포트폴리오입니다.

## 핵심 구성

- Python 3.11, Selenium 4.46, pytest
- requests 기반 Supabase Auth/PostgREST/RPC 검증
- pytest-html 및 실패 스크린샷
- 역할별 계정과 자동 테스트 데이터 정리
- GitHub Actions Chrome Headless 회귀 실행
- UI 13개 + API 11개, 총 24개 자동화 테스트

## 구조

```text
docs/                         QA 산출물 6개
tests/
├── api/                      인증·입찰·종료·권한 API 테스트
├── data/                     비민감 공통 데이터
├── pages/                    Selenium Page Objects
├── ui/                       UI 회귀 테스트
├── utils/                    환경 설정·Supabase API client
└── conftest.py               WebDriver·계정·API fixtures
.github/workflows/            GitHub Actions
reports/                      pytest-html
screenshots/                  실패 증적
```

## 로컬 준비

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
npm ci
```

`.env.example`을 참고해 `.env`를 구성합니다. 판매자, 입찰자 A, 입찰자 B는 서로 다른 실제 테스트 계정이어야 합니다.

```dotenv
VITE_SUPABASE_URL=
VITE_SUPABASE_PUBLISHABLE_KEY=
BASE_URL=http://localhost:8080
HEADLESS=false

TEST_USER_EMAIL=
TEST_USER_PASSWORD=
TEST_SELLER_EMAIL=
TEST_SELLER_PASSWORD=
TEST_BIDDER_A_EMAIL=
TEST_BIDDER_A_PASSWORD=
TEST_BIDDER_B_EMAIL=
TEST_BIDDER_B_PASSWORD=
```

## 실행

첫 번째 터미널:

```powershell
npm run dev
```

두 번째 터미널:

```powershell
pytest tests
pytest tests -m p0
pytest tests -m ui
pytest tests -m api
```

결과는 `reports/test-report.html`에 생성되며 UI 테스트 실패 시 `screenshots/`에 증적을 저장합니다.

## CI Secrets

`.env.example`의 Supabase 값과 모든 `TEST_*` 값을 GitHub repository secrets에 같은 이름으로 등록합니다. 이후 `QA Regression` workflow를 수동 실행하거나 main push/PR로 실행할 수 있습니다.

상세 요구사항, 위험, 시나리오, 테스트 케이스, 자동화 기준 및 결과는 `docs/01`~`06` 문서를 참고합니다.

기존 커밋에 `.venv`가 포함되어 있다면 `.gitignore`만으로는 추적이 해제되지 않습니다. 최초 1회 다음 명령으로 Git 인덱스에서만 제거합니다. 로컬 가상환경 파일은 삭제되지 않습니다.

```powershell
git rm -r --cached .venv
```
