# 자동화 계획

## 1. 자동화 목표

반복 실행 가치가 높고 결과가 명확한 핵심 회귀 흐름을 Playwright로 자동화한다.

자동화의 목적은 모든 테스트를 코드로 전환하는 것이 아니라, 핵심 기능 변경 시 빠르게 이상 여부를 판단할 수 있는 회귀 안전망을 구축하는 것이다.

---

## 2. 자동화 선정 기준

다음 조건을 만족하는 항목을 우선 자동화한다.

- 반복 실행 빈도가 높다.
- 결과가 명확하게 Pass/Fail로 구분된다.
- P0 또는 P1 기능이다.
- 사용자 핵심 흐름에 포함된다.
- 테스트 데이터와 실행 환경을 안정적으로 준비할 수 있다.

---

## 3. UI 자동화 대상

| 기능 | 자동화 항목 | 우선순위 |
|---|---|---|
| 로그인 | 정상 로그인, 보호 화면 접근 차단 | P1 |
| 상품 등록 | 정상 등록, 종료 시간 검증 | P1 |
| 상품 조회 | 목록·상세 정보 일치 | P1 |
| 입찰 | 정상 입찰, 최고가 이하 입찰, 종료 후 입찰 차단 | P0 |
| 낙찰 | 경매 종료 상태, 유찰, 거래 정보 권한 | P0 |
| 마이페이지 | 사용자별 내역 조회 | P1 |
| 좋아요 | 추가 및 해제 | P2 |

---

## 4. API 자동화 대상

- 정상·실패 로그인
- 상품 등록 요청 유효성
- 정상 입찰
- 최고가 이하 입찰
- 중복 입찰 요청
- 동시 입찰
- 종료 이후 입찰
- 최고 입찰자 낙찰 검증
- 거래 정보 접근 권한
- 다른 사용자 데이터 접근 차단

동시성, 상태 전환, 권한 검증은 UI보다 API 테스트가 더 빠르고 안정적으로 검증할 수 있으므로 API 자동화를 우선한다.

---

## 5. 수동 테스트 유지 대상

- 오류 메시지의 이해도
- 반응형 UI와 시각적 품질
- 브라우저 저장소 및 쿠키 속성 점검
- 탐색적 테스트
- 실제 시간 경계에서의 비정형 조작
- 네트워크 지연과 사용자 연속 조작
- 개인정보 노출 범위 검토

---

## 6. 권장 디렉터리 구조

```text
tests/
├── ui/
│   ├── login.spec.ts
│   ├── item.spec.ts
│   ├── bidding.spec.ts
│   └── auction-close.spec.ts
├── api/
│   ├── auth-api.spec.ts
│   ├── bidding-api.spec.ts
│   └── auction-close-api.spec.ts
├── pages/
│   ├── login.page.ts
│   ├── item.page.ts
│   └── auction.page.ts
├── fixtures/
│   └── auth.fixture.ts
└── test-data/
    └── auction-data.ts
```

초기에는 복잡한 구조를 먼저 적용하지 않고, 테스트가 증가할 때 Page Object와 fixture를 분리한다.

---

## 7. 테스트 데이터 관리

다음 정보는 코드에 직접 작성하지 않는다.

- 테스트 계정 이메일
- 비밀번호
- 인증 토큰
- 외부 서비스 키

로컬에서는 `.env.test`, CI에서는 GitHub Actions Secrets를 사용한다.

예시:

```text
TEST_SELLER_EMAIL
TEST_SELLER_PASSWORD
TEST_BIDDER_A_EMAIL
TEST_BIDDER_A_PASSWORD
TEST_BIDDER_B_EMAIL
TEST_BIDDER_B_PASSWORD
```

`.env*` 파일은 `.gitignore`에 포함한다.

---

## 8. Playwright 작성 기준

- 테스트 이름에 행동과 기대 결과를 포함한다.
- role, label, `data-testid` 기반 locator를 우선 사용한다.
- `waitForTimeout`을 사용하지 않는다.
- 각 테스트는 독립적으로 실행 가능해야 한다.
- 다른 테스트가 만든 상태에 의존하지 않는다.
- 실패 시 screenshot, trace, HTML report를 남긴다.
- 동일 테스트를 반복 실행해도 결과가 안정적이어야 한다.

---

## 9. CI 실행 기준

GitHub Actions에서 다음 순서로 실행한다.

1. 의존성 설치
2. Playwright 브라우저 설치
3. 애플리케이션 실행 또는 테스트 서버 연결
4. Smoke Test 실행
5. 핵심 회귀 테스트 실행
6. 실패 시 HTML Report와 trace 업로드

---

## 10. 자동화 완료 기준

- P0 자동화 테스트 100% 통과
- 로컬과 GitHub Actions 결과 일치
- 테스트 계정 정보가 저장소에 노출되지 않음
- 실패 시 원인을 확인할 수 있는 증적 생성
- 주요 테스트가 독립적으로 실행됨
