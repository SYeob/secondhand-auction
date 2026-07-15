# 테스트 결과 보고서

## 1. 수행 개요

| 항목 | 내용 |
|---|---|
| 프로젝트 | Pa-Bi Auction QA Automation Portfolio |
| 기준일 | 2026-07-15 |
| 환경 | Windows 11, Python 3.11, Chrome 150, Vite 8080 |
| 자동화 | Selenium, pytest, requests, pytest-html |
| 전체 구현 | UI 13개 + API 11개 = 24개 |
| CI | GitHub Actions workflow 구현, Secrets 등록 후 실행 필요 |

## 2. 실행 현황

대화에서 로컬 실행이 확인된 기존 테스트와 이번 일괄 구현 항목을 구분한다. 미실행 항목을 Pass로 계산하지 않는다.

| 구분 | 구현 | 실행 확인 | Pass | 실행 대기 |
|---|---:|---:|---:|---:|
| UI 기존 범위 | 9 | 9 | 9 | 0 |
| UI 추가 범위 | 4 | 0 | 0 | 4 |
| API | 11 | 0 | 0 | 11 |
| 합계 | 24 | 9 | 9 | 15 |

기존 확인 범위: Smoke 1, 로그인 3, 상품 등록 1, 입찰 UI 4.

## 3. 기능별 구현 상태

| 기능 | 구현 상태 | 검증 계층 | 비고 |
|---|---|---|---|
| 로그인 | 완료 | UI/API | 정상·실패·보호 화면 |
| 상품 등록 | 완료 | UI | 고유 데이터 생성·삭제 |
| 입찰 | 완료 | UI/API | 정상·이하 금액·순차·동시 |
| 경매 종료 | 완료 | UI/API | 종료 버튼·서버 차단 |
| 낙찰자 | 완료 | UI/API | 최고 금액·사용자 |
| 연락처 권한 | 완료 | UI/RPC | 낙찰자·비낙찰자·익명 |
| 마이페이지 | 완료 | UI | 본인 입찰 상품 |
| 좋아요 | 완료 | UI | 추가·조회·해제 |

## 4. 결함 현황

| ID | 제목 | 심각도 | 상태 | 우회 방법 |
|---|---|---|---|---|
| DEF-001 | 이미지 URL 선택 안내와 DB NOT NULL 제약 불일치 | Medium | Open | 자동화 데이터에 유효 URL 입력 |
| DEF-002 | 익명 REST API에서 seller_phone 직접 조회 가능 | Critical | Open | 없음, DB 권한 수정 필요 |

### DEF-001 재현

1. 로그인 후 상품 등록 화면으로 이동한다.
2. 별표 필수 항목을 모두 입력하고 이미지 URL은 비운다.
3. 상품 등록을 시도한다.
4. 화면 안내는 기본 이미지 적용을 약속하지만 DB 저장에 실패할 수 있다.

### DEF-002 재현 및 판정

1. 공개 배포 번들의 Supabase publishable key로 익명 요청을 구성한다.
2. `products?select=seller_phone&limit=1`을 호출한다.
3. 실제 결과는 HTTP 200이며 컬럼 접근이 허용된다.
4. 기대 결과는 401/403이다.

애플리케이션 UI가 연락처 컬럼을 선택하지 않는 것은 접근 통제가 아니다. 테이블 단위 SELECT 권한을 제거한 뒤 공개 컬럼만 다시 GRANT해야 한다.

권고 SQL 방향:

```sql
REVOKE SELECT ON public.products FROM anon, authenticated;

GRANT SELECT (
  id, title, description, location, category,
  starting_price, current_price, image_url, end_time,
  seller_id, created_at, updated_at
) ON public.products TO anon, authenticated;
```

판매자와 낙찰자의 `seller_phone` 조회는 기존 `get_own_product`, `get_seller_contact` RPC만 사용한다.

## 5. 자동화 실행 산출물

| 산출물 | 위치 |
|---|---|
| HTML 리포트 | `reports/test-report.html` |
| 실패 스크린샷 | `screenshots/` |
| CI 워크플로 | `.github/workflows/qa-regression.yml` |
| CI 증적 | GitHub Actions Artifact |

## 6. 잔여 위험

- 실제 운영 규모의 동시 입찰 부하와 DB 잠금 대기
- 중복 요청에 대한 명시적 idempotency key 부재
- 서버와 브라우저 간 시각 오차
- 종료 경매가 많을 때 낙찰 알림 조회 성능
- 모바일·다중 브라우저 호환성

## 7. 품질 의견

현재 자동화 구현은 완료됐지만 신규 15개 테스트의 실제 환경 실행과 GitHub Actions 검증이 남아 있고 Critical 개인정보 결함이 확인됐으므로 품질 판단은 `출시 보류`다.

다음 조건을 충족하면 완료로 전환한다.

- 전체 24개 회귀 테스트 실행
- P0 실패 원인 분석 및 Critical 결함 0건 확인
- Actions Secrets 등록 후 CI 성공
- DEF-001 수정 또는 요구사항 변경 결정
- DEF-002 DB 권한 수정 및 strict xfail 해제
