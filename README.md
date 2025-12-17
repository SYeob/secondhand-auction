# Pa-Bi Auction Platform - QA Automation Project

> **"사용자 경험을 보호하고 서비스의 무결성을 검증하는 QA 엔지니어링 포트폴리오"**
>
> 실시간 중고 경매 플랫폼 'Pa-Bi'의 품질 보증(QA)을 위해 구축한 **테스트 자동화 프레임워크** 리포지토리입니다.
> Python과 Selenium을 활용하여 UI/UX 시나리오를 자동화하고, Pytest 기반의 통합 테스트 환경을 구축했습니다.

<br>

## QA Tech Stack

| Category      | Technology                                                                                                | Usage                                              |
| :------------ | :-------------------------------------------------------------------------------------------------------- | :------------------------------------------------- |
| **Language**  | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)       | 테스트 스크립트 작성 및 자동화 로직 구현           |
| **Framework** | ![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white)       | 테스트 시나리오 관리, 실행 및 리포팅               |
| **E2E / UI**  | ![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=flat-square&logo=selenium&logoColor=white) | 웹 UI 기능 자동화 (로그인, 상품 탐색 등)           |
| **API Test**  | ![Requests](https://img.shields.io/badge/Requests-2CA5E0?style=flat-square&logo=python&logoColor=white)   | 백엔드 서버 상태 및 API 응답 검증                  |
| **Runner**    | ![Shell](https://img.shields.io/badge/Script-Test_Runner-orange?style=flat-square)                        | Python 기반의 Cross-Platform 통합 테스트 러너 구현 |

<br>

## Project Structure (QA Focused)

개발 소스 외에, 품질 검증을 위해 새롭게 구축한 QA 전용 디렉토리 구조입니다.

```bash
secondhand-auction/
├── run_tests.py         # 통합 테스트 실행기 (API + UI 테스트 일괄 수행 및 결과 리포팅)
├── tests/               # 테스트 자동화 코드 저장소
│   ├── api/             # API/서버 상태 검증 (Health Check, Status Code 검증)
│   └── ui/              # Selenium 기반 E2E 시나리오 (Login, Product View flow)
├── docs/
│   └── qa/              # QA 문서 산출물 (Test Cases, Bug Reports)
└── requirements.txt     # 테스트 환경 구성을 위한 의존성 패키지 목록


# Pa-Bi 경매 플랫폼 명세서

## 1. 프로젝트 개요

**Pa-Bi**는 한국어 기반 실시간 경매 플랫폼입니다. 사용자는 상품을 등록하고, 입찰하며, 낙찰받을 수 있습니다.

**URL:** https://syeob.lovable.app/

### 1.1 기술 스택
- **Frontend**: React 18, TypeScript, Vite
- **UI Framework**: Tailwind CSS, shadcn/ui
- **Backend**: Supabase (PostgreSQL, Auth, Realtime)
- **State Management**: TanStack React Query
- **Routing**: React Router DOM v6

---

## 2. 데이터베이스 스키마

### 2.1 profiles (사용자 프로필)
| 컬럼명 | 타입 | 설명 | 제약조건 |
|--------|------|------|----------|
| id | UUID | 사용자 ID (auth.users 참조) | PK |
| email | TEXT | 이메일 주소 | NOT NULL |
| username | TEXT | 사용자명 | NULLABLE |
| created_at | TIMESTAMPTZ | 생성일시 | DEFAULT now() |
| updated_at | TIMESTAMPTZ | 수정일시 | DEFAULT now() |

### 2.2 products (상품)
| 컬럼명 | 타입 | 설명 | 제약조건 |
|--------|------|------|----------|
| id | UUID | 상품 ID | PK, DEFAULT gen_random_uuid() |
| title | TEXT | 상품명 | NOT NULL, MAX 100자 |
| description | TEXT | 상품 설명 | NULLABLE, MAX 2000자 |
| location | TEXT | 거래 지역 | NOT NULL, MAX 100자 |
| category | TEXT | 카테고리 | NOT NULL, DEFAULT '전체' |
| starting_price | INTEGER | 시작가 | NOT NULL, 0~100억 |
| current_price | INTEGER | 현재가 | NOT NULL |
| image_url | TEXT | 상품 이미지 URL | NOT NULL |
| end_time | TIMESTAMPTZ | 경매 종료 시간 | NOT NULL |
| seller_id | UUID | 판매자 ID | NOT NULL |
| seller_phone | TEXT | 판매자 연락처 | NULLABLE |
| created_at | TIMESTAMPTZ | 생성일시 | DEFAULT now() |
| updated_at | TIMESTAMPTZ | 수정일시 | DEFAULT now() |

### 2.3 bids (입찰)
| 컬럼명 | 타입 | 설명 | 제약조건 |
|--------|------|------|----------|
| id | UUID | 입찰 ID | PK, DEFAULT gen_random_uuid() |
| product_id | UUID | 상품 ID | NOT NULL |
| user_id | UUID | 입찰자 ID | NOT NULL |
| bid_amount | INTEGER | 입찰 금액 | NOT NULL |
| created_at | TIMESTAMPTZ | 입찰 시간 | DEFAULT now() |

### 2.4 likes (좋아요)
| 컬럼명 | 타입 | 설명 | 제약조건 |
|--------|------|------|----------|
| id | UUID | 좋아요 ID | PK, DEFAULT gen_random_uuid() |
| user_id | UUID | 사용자 ID | NOT NULL |
| product_id | UUID | 상품 ID | NOT NULL |
| created_at | TIMESTAMPTZ | 생성일시 | DEFAULT now() |

---

## 3. Row Level Security (RLS) 정책

### 3.1 profiles
| 작업 | 정책 |
|------|------|
| SELECT | 모든 사용자 가능 (username만 공개) |
| INSERT | 본인만 가능 (auth.uid() = id) |
| UPDATE | 본인만 가능 (auth.uid() = id) |
| DELETE | 불가 |

### 3.2 products
| 작업 | 정책 |
|------|------|
| SELECT | 누구나 가능 |
| INSERT | 로그인 사용자 (auth.uid() = seller_id) |
| UPDATE | 판매자만 가능 (auth.uid() = seller_id) |
| DELETE | 판매자만 가능 (auth.uid() = seller_id) |

### 3.3 bids
| 작업 | 정책 |
|------|------|
| SELECT | 누구나 가능 |
| INSERT | 로그인 사용자 (auth.uid() = user_id) |
| UPDATE | 불가 |
| DELETE | 불가 |

### 3.4 likes
| 작업 | 정책 |
|------|------|
| SELECT | 누구나 가능 |
| INSERT | 로그인 사용자 (auth.uid() = user_id) |
| UPDATE | 불가 |
| DELETE | 본인만 가능 (auth.uid() = user_id) |

---

## 4. 데이터베이스 함수 및 트리거

### 4.1 validate_bid()
- **용도**: 입찰 유효성 검증 (BEFORE INSERT 트리거)
- **검증 항목**:
  - 경매 종료 여부 확인 (end_time > NOW())
  - 입찰 금액이 현재가보다 높은지 확인

### 4.2 update_product_price()
- **용도**: 입찰 시 상품 현재가 자동 업데이트 (AFTER INSERT 트리거)
- **동작**: 새 입찰이 현재가보다 높으면 current_price 업데이트

### 4.3 get_seller_contact(p_product_id UUID)
- **용도**: 낙찰자에게 판매자 연락처 제공
- **반환**: seller_phone, seller_id
- **접근 제한**: 경매 종료 후 낙찰자만 호출 가능

### 4.4 handle_new_user()
- **용도**: 회원가입 시 profiles 테이블 자동 생성
- **트리거**: auth.users INSERT 시 실행

---

## 5. 페이지 구조

### 5.1 / (홈페이지)
- 히어로 배너 (자동 슬라이드)
- 카테고리 네비게이션
- 상품 목록 (카테고리별 필터링)
- 검색 기능

### 5.2 /auth (인증)
- 로그인 / 회원가입 탭
- 이메일/비밀번호 인증
- 입력 검증 (Zod)

### 5.3 /product/:id (상품 상세)
- 상품 정보 표시
- 실시간 카운트다운 타이머
- 입찰 기능
- 실시간 입찰 내역 (Realtime 구독)
- 좋아요 기능
- 낙찰자 알림 및 판매자 연락처 확인

### 5.4 /register-product (상품 등록)
- 상품 정보 입력 폼
- 이미지 URL 입력
- 카테고리 선택
- 경매 종료 시간 설정

### 5.5 /my-page (마이페이지)
- 응찰한 상품 목록
- 좋아요한 상품 목록

---

## 6. 핵심 기능 명세

### 6.1 인증 시스템
```

회원가입:

- 이메일 형식 검증
- 사용자명: 2~20자
- 비밀번호: 최소 6자
- 가입 시 profiles 테이블 자동 생성

로그인:

- 이메일/비밀번호 인증
- 세션 기반 상태 관리
- 자동 리다이렉트 (로그인 후 홈)

```

### 6.2 상품 등록
```

필수 입력:

- 상품명 (최대 100자)
- 거래 지역 (최대 100자)
- 카테고리 (전체/패션/디지털/가전/생활/기타)
- 시작가 (0~100억원)
- 경매 종료 시간

선택 입력:

- 상품 설명 (최대 2000자)
- 이미지 URL (기본값: /placeholder.svg)
- 판매자 연락처 (010-XXXX-XXXX 형식)

```

### 6.3 입찰 시스템
```

입찰 조건:

- 로그인 필수
- 입찰 금액 > 현재가
- 경매 진행 중 (end_time > NOW())
- 최대 입찰가: 100억원

입찰 프로세스:

1. 클라이언트 유효성 검증
2. DB 트리거 (validate_bid) 재검증
3. 입찰 성공 시 current_price 자동 업데이트
4. 실시간 브로드캐스트 (Realtime)

```

### 6.4 낙찰 시스템
```

낙찰자 결정:

- 경매 종료 후 (end_time <= NOW())
- 최고 입찰자 = 낙찰자
- 동일 금액 시 먼저 입찰한 사용자 우선

낙찰자 UI:

- "🎉 축하드립니다. 낙찰되었습니다! 🎉" 배너
- "클릭하여 판매자 연락처 확인" 버튼
- get_seller_contact RPC로 연락처 조회

```

### 6.5 실시간 기능
```

Realtime 구독:

- bids 테이블 INSERT 이벤트
- 새 입찰 시 즉시 UI 업데이트
- 입찰 내역 자동 갱신

```

### 6.6 좋아요 기능
```

동작:

- 로그인 사용자만 가능
- 토글 방식 (좋아요/취소)
- likes 테이블에 저장
- 마이페이지에서 목록 확인

````

---

## 7. API 엔드포인트

### 7.1 인증
| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| POST | /auth/v1/signup | 회원가입 |
| POST | /auth/v1/token?grant_type=password | 로그인 |
| GET | /auth/v1/user | 현재 사용자 정보 |
| POST | /auth/v1/logout | 로그아웃 |

### 7.2 상품
| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| GET | /rest/v1/products | 전체 상품 조회 |
| GET | /rest/v1/products?category=eq.{category} | 카테고리별 조회 |
| GET | /rest/v1/products?id=eq.{id} | 상품 상세 조회 |
| POST | /rest/v1/products | 상품 등록 (인증 필요) |
| PATCH | /rest/v1/products?id=eq.{id} | 상품 수정 (판매자만) |
| DELETE | /rest/v1/products?id=eq.{id} | 상품 삭제 (판매자만) |

### 7.3 입찰
| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| GET | /rest/v1/bids?product_id=eq.{id} | 상품별 입찰 내역 |
| POST | /rest/v1/bids | 입찰하기 (인증 필요) |
| GET | /rest/v1/bids?user_id=eq.{id} | 사용자 입찰 내역 |

### 7.4 좋아요
| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| POST | /rest/v1/likes | 좋아요 추가 |
| DELETE | /rest/v1/likes?id=eq.{id} | 좋아요 삭제 |
| GET | /rest/v1/likes?user_id=eq.{id} | 사용자 좋아요 목록 |

### 7.5 RPC
| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| POST | /rest/v1/rpc/get_seller_contact | 판매자 연락처 조회 (낙찰자만) |

---

## 8. 카테고리 목록

| 코드 | 표시명 |
|------|--------|
| 전체 | 전체 |
| 패션 | 패션 |
| 디지털 | 디지털 |
| 가전 | 가전 |
| 생활 | 생활 |
| 기타 | 기타 |

---

## 9. 입력 검증 규칙 (Zod)

### 9.1 상품 등록
```typescript
{
  title: string, max 100자, 필수
  description: string, max 2000자, 선택
  location: string, max 100자, 필수
  category: enum, 필수
  starting_price: number, 0~100억, 필수
  image_url: url format, 선택
  seller_phone: 010-XXXX-XXXX format, 선택
  end_time: datetime, 필수
}
````

### 9.2 입찰

```typescript
{
  bid_amount: number, > current_price, max 100억
  product_id: uuid, 필수
}
```

### 9.3 회원가입

```typescript
{
  email: email format, 필수
  username: string, 2~20자, 필수
  password: string, min 6자, 필수
}
```

---

## 10. 파일 구조

```
src/
├── components/
│   ├── ui/              # shadcn/ui 컴포넌트
│   ├── CategoryNav.tsx  # 카테고리 네비게이션
│   ├── Header.tsx       # 헤더
│   ├── Hero.tsx         # 히어로 배너
│   ├── ProductCard.tsx  # 상품 카드
│   ├── ProductSection.tsx # 상품 섹션
│   ├── SellerContactInfo.tsx # 판매자 연락처
│   └── WinnerNotification.tsx # 낙찰 알림
├── pages/
│   ├── Index.tsx        # 홈페이지
│   ├── Auth.tsx         # 인증 페이지
│   ├── ProductDetail.tsx # 상품 상세
│   ├── RegisterProduct.tsx # 상품 등록
│   ├── MyPage.tsx       # 마이페이지
│   └── NotFound.tsx     # 404 페이지
├── integrations/
│   └── supabase/
│       ├── client.ts    # Supabase 클라이언트
│       └── types.ts     # 타입 정의
├── hooks/
│   ├── use-mobile.tsx   # 모바일 감지
│   └── use-toast.ts     # 토스트 알림
├── lib/
│   └── utils.ts         # 유틸리티 함수
├── assets/              # 이미지 에셋
├── App.tsx              # 라우터 설정
├── main.tsx             # 진입점
└── index.css            # 글로벌 스타일
```

---

## 11. 환경 변수

```
VITE_SUPABASE_URL=https://cysqofttgfckhhcifzsb.supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 12. 버전 정보

- **문서 버전**: 1.0.0
- **최종 업데이트**: 2025-12-17
- **프로젝트 상태**: 개발 중 (포트폴리오 프로젝트)
