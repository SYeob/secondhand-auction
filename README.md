# Pa-Bi 경매 플랫폼 — 기획 및 개발 요구사항 명세서
**문서 버전**: 2.0.0  
**최종 업데이트**: 2026-07-13  
**프로젝트 상태**: 개발 중 (포트폴리오)
---
## 1. 프로젝트 개요
### 1.1 서비스 소개
**Pa-Bi**는 한국어 사용자를 위한 실시간 C2C(개인간 거래) 경매 플랫폼입니다.
누구나 상품을 등록하고, 로그인 사용자는 실시간으로 입찰하며, 경매가 종료되면 최고가 입찰자가 낙찰되어 판매자와 직접 연락할 수 있습니다.
### 1.2 목표
- **간단한 등록/입찰 UX**로 누구나 부담 없이 경매에 참여
- **실시간 입찰 반영**으로 몰입감 있는 경매 경험 제공
- **안전한 개인정보 보호**: 연락처는 낙찰자에게만, 이메일은 완전 비공개
- **AI 에이전트 연동(MCP)**을 통한 확장 가능한 인터페이스
### 1.3 타겟 사용자
- 중고 물품을 경매 방식으로 판매하려는 개인 판매자
- 원하는 물건을 합리적인 가격에 구매하려는 입찰 사용자
- 자동화된 도구/에이전트(Claude, Cursor 등)로 경매를 탐색·입찰하려는 파워 유저
---
## 2. 기능 요구사항
### 2.1 인증 (Auth)
| ID | 요구사항 | 우선순위 |
|----|----------|---------|
| A-1 | 이메일/비밀번호 회원가입 (username 2~20자, password ≥ 6자) | 필수 |
| A-2 | 이메일/비밀번호 로그인 및 세션 유지 | 필수 |
| A-3 | 로그아웃 | 필수 |
| A-4 | 가입 시 `profiles` 레코드 자동 생성 (트리거) | 필수 |
| A-5 | 유출된 비밀번호 차단(HIBP) | 필수 |
| A-6 | OAuth 소셜 로그인 미지원 (정책) | — |
### 2.2 상품 관리
| ID | 요구사항 | 우선순위 |
|----|----------|---------|
| P-1 | 상품 등록 (제목, 설명, 지역, 카테고리, 시작가, 종료시간, 이미지 URL, 연락처) | 필수 |
| P-2 | 판매자 본인만 상품 수정/삭제 | 필수 |
| P-3 | 홈에서 카테고리별 필터링 및 검색 | 필수 |
| P-4 | 상품 상세 페이지: 정보, 카운트다운, 입찰 UI, 실시간 입찰 로그 | 필수 |
| P-5 | 상품 이미지 미지정 시 `/placeholder.svg` 대체 | 필수 |
### 2.3 입찰 (Bidding)
| ID | 요구사항 | 우선순위 |
|----|----------|---------|
| B-1 | 로그인 사용자만 입찰 가능 | 필수 |
| B-2 | 입찰 금액은 현재가보다 커야 함 (DB 트리거 재검증) | 필수 |
| B-3 | 경매 종료 후 입찰 불가 | 필수 |
| B-4 | 새 입찰 시 `products.current_price` 자동 갱신 | 필수 |
| B-5 | Supabase Realtime으로 입찰 내역 즉시 반영 | 필수 |
| B-6 | 입찰 최대 금액 100억 원 (실수 방지) | 필수 |
### 2.4 낙찰 (Winning)
| ID | 요구사항 | 우선순위 |
|----|----------|---------|
| W-1 | 종료 후 최고 입찰자를 낙찰자로 표시 | 필수 |
| W-2 | 낙찰자에게만 축하 배너 및 연락처 확인 버튼 노출 | 필수 |
| W-3 | `get_seller_contact` RPC로 연락처 조회 (낙찰자 검증) | 필수 |
### 2.5 좋아요 & 마이페이지
| ID | 요구사항 | 우선순위 |
|----|----------|---------|
| L-1 | 상품 좋아요 토글 (로그인 필요) | 필수 |
| M-1 | 마이페이지: 응찰한 상품 / 좋아요한 상품 탭 | 필수 |
### 2.6 타이머
| ID | 요구사항 | 우선순위 |
|----|----------|---------|
| T-1 | 상품 카드/상세에 실시간 카운트다운 | 필수 |
| T-2 | 타이머가 0에 도달하면 원래 종료 시간 기준으로 반복 재시작 (데모용 루프) | 필수 |
### 2.7 AI 에이전트 통합 (MCP)
| ID | 요구사항 | 우선순위 |
|----|----------|---------|
| MCP-1 | `list_products`, `get_product` — 비인증 조회 | 필수 |
| MCP-2 | `list_my_bids`, `place_bid` — OAuth 인증 필요 | 필수 |
| MCP-3 | OAuth Consent 화면 `/​.lovable/oauth/consent` 제공 | 필수 |
---
## 3. 비기능 요구사항
### 3.1 보안
- 모든 `public` 테이블에 RLS 활성화 및 명시적 `GRANT`
- `profiles.email`은 어떤 클라이언트 역할도 SELECT 불가
- `products.seller_phone`은 소유자(RPC) 또는 낙찰자(RPC)만 접근
- 사용자 역할은 별도 테이블에 저장 (권한 상승 방지)
- SECURITY DEFINER 함수는 anon/authenticated에서 직접 실행 불가
- Zod 기반 클라이언트 입력 검증 + DB 트리거 서버 검증(이중)
### 3.2 성능
- Vite 빌드 기반 SPA, 코드 스플리팅
- React Query로 데이터 캐싱 및 stale-while-revalidate
- Supabase Realtime 채널 최소화 (상품 상세에서만 구독)
### 3.3 접근성 & UX
- 시맨틱 HTML + shadcn/ui 기반 접근성 컴포넌트
- 반응형: 모바일/태블릿/데스크톱
- 라우트 변경 시 스크롤 최상단 이동
- 검색 바는 홈에서만 노출
### 3.4 SEO
- `<title>`, `<meta description>`, OG/Twitter 태그 설정
- 단일 H1, 시맨틱 마크업
---
## 4. 데이터 모델 요약
| 테이블 | 핵심 컬럼 | 비고 |
|--------|----------|------|
| `profiles` | id, email, username | email은 컬럼 단위 SELECT 차단 |
| `products` | id, title, category, starting_price, current_price, end_time, seller_id, seller_phone | seller_phone SELECT 차단 |
| `bids` | id, product_id, user_id, bid_amount | INSERT only |
| `likes` | id, product_id, user_id | 사용자 본인만 DELETE |
주요 RPC: `get_seller_contact`, `get_own_product`  
주요 트리거: `handle_new_user`, `validate_bid`, `update_product_price`
*상세 스키마·RLS·API는 `docs/PROJECT_SPECIFICATION.md` 참조.*
---
## 5. 화면(라우트) 요구사항
| 경로 | 화면 | 주요 기능 |
|------|------|----------|
| `/` | 홈 | 히어로, 카테고리, 상품 목록, 검색 |
| `/auth` | 로그인/회원가입 | Zod 검증, `next` 리다이렉트 지원 |
| `/product/:id` | 상품 상세 | 카운트다운, 입찰, 실시간 로그, 낙찰 UI |
| `/register-product` | 상품 등록/수정 | 판매자 전용 |
| `/my-page` | 마이페이지 | 응찰/좋아요 목록 |
| `/.lovable/oauth/consent` | MCP OAuth 동의 | 에이전트 연결 승인 |
| `*` | 404 | Not Found |
---
## 6. 기술 스택
- **Frontend**: React 18, TypeScript, Vite 5, Tailwind CSS 3, shadcn/ui
- **상태/데이터**: TanStack React Query, React Hook Form + Zod
- **Backend**: Lovable Cloud (PostgreSQL, Auth, Realtime, Edge Functions, Storage)
- **AI 통합**: `@lovable.dev/mcp-js` (MCP 서버, OAuth 인증)
- **라우팅**: React Router DOM v6
---
## 7. 개발 규칙
1. **디자인 토큰**: 모든 색상/그라디언트는 `index.css` 시맨틱 토큰 사용. `text-white`, `bg-black`, `bg-[#...]` 등 하드코딩 금지.
2. **자동 생성 파일 편집 금지**: `src/integrations/supabase/client.ts`, `types.ts`, `.env`, `supabase/config.toml`.
3. **RLS 우선**: 새 테이블 생성 시 반드시 RLS 정책과 `GRANT` 함께 정의.
4. **역할 저장 위치**: 사용자 권한은 `profiles`가 아닌 별도 `user_roles` 테이블 (미래 확장 대비).
5. **Mock 데이터 금지**: 항상 DB에서 조회.
6. **에러 로깅**: 민감 정보(email, phone, token) 콘솔 출력 금지.
---
