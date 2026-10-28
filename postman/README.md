# Pa-Bi Postman 핵심 입찰 검증

## 가져오기와 첫 실행

1. Postman에서 **Import**를 눌러 `pabi-core-bidding.postman_collection.json`을 가져옵니다.
2. **Pa-Bi Core Bidding TC → Variables**를 열고 아래 6개 값을 로컬 값에 입력합니다. 공유 값으로 게시하거나 계정을 입력한 Collection을 Git에 올리지 마세요.

   | 변수 | 값 |
   |---|---|
   | `seller_email`, `seller_password` | 판매자 테스트 계정 |
   | `bidder_a_email`, `bidder_a_password` | 입찰자 A 테스트 계정 |
   | `bidder_b_email`, `bidder_b_password` | 입찰자 B 테스트 계정 |

   미리 가입하고 필요한 이메일 인증을 완료한 **서로 다른 계정 3개**가 필요합니다. Collection은 사용자를 새로 가입시키거나 계정을 수정하지 않습니다. `base_url`과 공개 `anon_key`는 기존 프로젝트 Collection의 값입니다. 서버가 바뀌었다면 해당 테스트 환경의 공개 값으로 교체합니다. `service_role` 키는 사용하지 않습니다. 다른 Environment가 같은 변수명을 덮어쓰지 않도록 첫 실행은 **No environment**로 선택합니다.

3. Collection의 **Run collection / Run**으로 실행합니다. `00 준비`부터 마지막 요청까지 모두 선택하고 **Iterations 1**, **Delay 500ms**로 시작합니다. 스크립트/테스트 실패로 즉시 중지하는 옵션이 있다면 끄고, 정리 요청까지 실행합니다.
4. Run 결과에서 각 폴더 마지막의 **`TC-… 종합 판정: 준비·검증·정리 모두 성공`**을 확인합니다. 개별 요청의 `Send` 성공과 TC 전체 PASS는 다릅니다.
5. 실패 항목을 열어 상태 코드, 응답 Body, 실패한 assertion을 비교합니다. 비밀번호·토큰이 포함된 인증 응답은 증적으로 공유하지 않습니다.

현재 배포된 서버가 활성 상태인지와 계정은 사용자가 확인해야 합니다. 최초 Import만으로 서버 테스트가 이미 통과한 것은 아닙니다.

## 구성과 검증 범위

**8개 TC / 9개 입력 조건**, 전체 요청 68개입니다. `TC-BID-002`의 EQUAL/LOWER는 서로 다른 TC가 아니라 한 TC의 두 데이터 조건입니다.

| TC | 폴더 | 기대 결과 |
|---|---|---|
| TC-BID-001 | 정상 입찰 | 15,000원, 입찰자 A, 입찰 1건 |
| TC-BID-002 | EQUAL / LOWER | 10,000원 / 9,000원 거부, 현재가 10,000원 유지, 입찰 0건 |
| TC-BID-003 | 순차 입찰 | A 15,000원 → B 20,000원, 현재가 20,000원, 입찰 2건, 최고 입찰자 B |
| TC-CLOSE-001 | 종료 후 입찰 | 종료 상태 준비 후 거부, 현재가 유지, 입찰 0건 |
| TC-BID-004 | 익명 입찰 | 로그인 토큰 없이 요청 거부, 상태 유지 |
| TC-BID-005 | 잘못된 토큰 | 인증 거부, 상태 유지 |
| TC-BID-006 | 사용자 ID 위조 | A의 토큰에 B의 사용자 ID를 보내면 거부, 상태 유지 |
| TC-BID-007 | 금액 누락 | `bid_amount` 누락 요청 거부, 상태 유지 |

실제 요청 수는 Collection에서 확인할 수 있으며 생성기가 변경되면 함께 갱신합니다. 동시 입찰은 이 Postman Collection 범위에 포함하지 않습니다. 기존 Python `ThreadPoolExecutor` 테스트를 사용합니다. 종료 테스트는 새 상품의 종료 시각을 과거로 바꾸어 종료 상태를 준비하며, 실제 종료 경계 시각을 기다리는 검증은 아닙니다.

## 요청과 TC의 관계

각 폴더는 **신규 상품 생성 → 검증할 입찰 → 상품 재조회 → 입찰 내역 조회 → 상품 삭제 → 상품/입찰 삭제 확인 → 종합 판정** 흐름입니다. 필요한 경우 입찰 B 요청 또는 종료 상태 준비가 추가됩니다.

- 생성 상품은 `QA-POSTMAN-<TC ID>-<UUID>` 이름으로 식별합니다.
- 상품 생성 때 확인한 ID·판매자·고유 이름을 모두 지정해 삭제하므로 기존 상품을 삭제 대상으로 삼지 않습니다.
- 준비 실패는 `BLOCKED` 검증 실패로 표시하고 관련 요청을 건너뜁니다. 건너뜀을 PASS로 집계하지 않습니다.
- 요청 거부 시 상태 코드뿐 아니라 오류 코드를 확인해 단순 JSON 오류 등으로 잘못 통과하지 않게 합니다. 업무 오류는 메시지도 확인합니다.
- 종합 판정은 모든 필수 요청의 실행 여부와 앞선 assertion 실패를 확인합니다. 일부 요청만 선택해 실행했다면 정규 TC 결과로 기록하지 않습니다.
- 삭제 응답만 믿지 않고 상품 및 관련 입찰이 실제로 조회되지 않는지도 확인합니다.
- 상태 변경 결과는 REST 재조회로 검증합니다. 직접 SQL 조회를 했다고 표현하지 않습니다.

## 실행 방식의 주의점

토큰·사용자 ID·상품 ID는 **`pm.variables` 실행 로컬 변수**입니다. 같은 Collection Run 내에서만 이어지며, 서로 다른 요청에 `Send`를 따로 눌러도 세션과 상품 ID가 자동으로 이어지지는 않습니다. 처음에는 Collection 전체를 Runner로 실행하세요. Collection을 두 번 동시에 실행하지 마세요.

테스트가 실패해도 Runner가 끝까지 실행되면 정리를 시도합니다. 앱 종료·네트워크 중단·토큰 만료 등으로 실행 자체가 중단되면 정리를 보장할 수 없습니다. 잔존 상품은 본인 판매자 계정에서 이번 실행의 `QA-POSTMAN-` 고유 이름을 대조해 개별 삭제하세요. 전체 상품 삭제 요청으로 대체하지 마세요.

준비 또는 서버 환경 문제로 막힌 경우는 `BLOCKED`, 실제 검증에서 요구사항을 충족하지 못한 경우는 `FAIL`, 검증과 정리가 모두 성공한 경우에만 `PASS`입니다. Postman에서 준비 실패가 빨간 assertion으로 보이더라도 제품 결함으로 바로 등록하지 않습니다.

## 문서·코드·결과 연결

- 케이스 기준: [`docs/04_TEST_CASES.md`](../docs/04_TEST_CASES.md)
- Postman 상세 매핑: [`docs/07_POSTMAN_CORE_CASES.md`](../docs/07_POSTMAN_CORE_CASES.md)
- 실행 기록 양식: [`docs/test-runs/postman-core-template.md`](../docs/test-runs/postman-core-template.md)
- 기존 Python: [`tests/api/test_bidding_api.py`](../tests/api/test_bidding_api.py), [`tests/api/test_auction_close_api.py`](../tests/api/test_auction_close_api.py)

계정 정보를 입력하기 전의 깨끗한 JSON만 Git에 저장합니다. 수동 편집 대신 `python3 postman/build_core_collection.py`로 재생성합니다. 입력 파일은 기존 `pabi-auction-api.postman_collection.json`이며 기존 Collection은 변경하지 않습니다.

로컬 모의 응답 검증: `node postman/validate_core_collection.cjs`. 이는 스크립트의 정상 판정·오검출 방지·정리 검증을 확인하며 실제 Supabase 실행 결과가 아닙니다.
