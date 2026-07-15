# 자동화 계획

## 1. 자동화 목표와 선정 기준

반복 실행 가치가 높고 결과가 명확한 P0/P1 흐름을 회귀 안전망으로 만든다. 모든 항목을 UI로 작성하지 않고 검증 책임에 따라 UI와 API를 분리한다.

- UI: 사용자 조작, 안내 문구, 화면 상태, 목록 반영
- API: 입찰 원자성, 서버 검증, 낙찰 계산, RLS/RPC 권한
- 수동: 시각 품질, 탐색적 연속 조작, 실제 네트워크·시간 경계

## 2. 자동화 구조

```text
tests/
├── api/
│   ├── test_auth_api.py
│   ├── test_bidding_api.py
│   └── test_auction_close_api.py
├── data/
│   └── test_data.py
├── pages/
│   ├── base_page.py
│   ├── login_page.py
│   ├── register_product_page.py
│   ├── auction_page.py
│   └── my_page.py
├── ui/
│   ├── test_smoke.py
│   ├── test_login.py
│   ├── test_product_registration.py
│   ├── test_bidding.py
│   ├── test_auction_close.py
│   ├── test_my_page.py
│   └── test_likes.py
├── utils/
│   ├── config.py
│   └── supabase_api.py
└── conftest.py
```

## 3. 테스트 데이터 전략

1. 역할별 계정을 `.env` 또는 Actions Secrets에서 읽는다.
2. API로 테스트에 필요한 상품·입찰을 빠르게 준비한다.
3. 고유 상품명으로 병렬 실행 충돌을 방지한다.
4. `yield` fixture 또는 `finally`에서 생성 상품을 삭제한다.
5. 상품 삭제 cascade로 관련 입찰·좋아요를 정리한다.

필수 역할:

```dotenv
TEST_USER_EMAIL=
TEST_USER_PASSWORD=
TEST_SELLER_EMAIL=
TEST_SELLER_PASSWORD=
TEST_BIDDER_A_EMAIL=
TEST_BIDDER_A_PASSWORD=
TEST_BIDDER_B_EMAIL=
TEST_BIDDER_B_PASSWORD=
```

## 4. 안정성 기준

- `time.sleep`은 경매 종료라는 외부 상태 전환 대기에만 제한적으로 사용한다.
- 일반 UI 동기화는 WebDriverWait과 expected conditions를 사용한다.
- Chrome 비밀번호 저장·유출 경고는 테스트 프로필 설정으로 비활성화한다.
- 각 UI 테스트는 새로운 Chrome 인스턴스를 사용한다.
- 실패 시 함수 본문 단계에서 스크린샷을 저장한다.
- 비밀번호와 access token은 출력하지 않는다.

## 5. 실행 명령

```powershell
# Vite 서버
npm run dev

# 전체 회귀
pytest -c tests/pytest.ini tests

# 선택 실행
pytest -c tests/pytest.ini tests -m smoke
pytest -c tests/pytest.ini tests -m p0
pytest -c tests/pytest.ini tests -m ui
pytest -c tests/pytest.ini tests -m api
```

## 6. GitHub Actions

`.github/workflows/qa-regression.yml`에서 다음을 수행한다.

1. Node/Python 환경 구성
2. 프론트 빌드
3. Vite 서버 실행과 HTTP 준비 확인
4. Chrome Headless 전체 회귀
5. HTML 리포트, 실패 스크린샷, Vite 로그 업로드

Secrets에는 Supabase 설정과 역할별 계정만 저장한다. Artifact 보존 기간은 14일이다.

## 7. 완료 기준

- 구현된 24개 테스트 전체 수집
- P0 자동화 Pass 또는 명확한 결함 연결
- 테스트 데이터 잔존 없음
- 로컬·CI 동일 테스트 명령 사용
- 실패 원인을 HTML·스크린샷·로그에서 확인 가능
