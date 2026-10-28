"""Generate the independently importable Postman bidding regression collection."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = json.loads((HERE / 'pabi-auction-api.postman_collection.json').read_text())
PUBLIC = {v['key']: v.get('value', '') for v in SOURCE['variable']}

HELPER = '''function check(name, fn) {
  pm.test(name, function () {
    try { fn(); }
    catch (error) { pm.variables.set("qa_case_failed", true); throw error; }
  });
}
function rows() { const data = pm.response.json(); pm.expect(data).to.be.an("array"); return data; }
'''

def event(kind, script):
    return {'listen': kind, 'script': {'type': 'text/javascript', 'exec': script.strip().splitlines()}}

def request(name, method, path, body=None, role='seller', pre='', post='', guard=True, description=''):
    headers = [{'key': 'apikey', 'value': '{{anon_key}}'}]
    if role:
        token = '{{qa_' + role + '_token}}' if role != 'invalid' else 'invalid.test.token'
        headers.append({'key': 'Authorization', 'value': 'Bearer ' + token})
    if method in ('POST', 'PATCH'):
        headers += [{'key': 'Content-Type', 'value': 'application/json'},
                    {'key': 'Prefer', 'value': 'return=representation'}]
    r = {'method': method, 'header': headers, 'url': '{{base_url}}' + path,
         'auth': {'type': 'noauth'}, 'description': description}
    if body is not None:
        r['body'] = {'mode': 'raw', 'raw': json.dumps(body, ensure_ascii=False, indent=2),
                     'options': {'raw': {'language': 'json'}}}
    # Numeric values are substituted without quotes in raw JSON.
    if body is not None:
        r['body']['raw'] = r['body']['raw'].replace('"{{qa_amount}}"', '{{qa_amount}}')
    if guard:
        pre = '''if (!pm.variables.get("qa_product_created") || !pm.variables.get("qa_product_id")) {
  pm.variables.set("qa_case_failed", true);
  pm.test("BLOCKED: 상품 준비 실패 - TC 통과로 집계하지 않음", function () { throw new Error("Run collection from 00 준비. Check creation response."); });
  pm.execution.skipRequest();
}
''' + pre
    events = []
    if pre: events.append(event('prerequest', pre))
    if post:
        post += '\nconst completed = JSON.parse(pm.variables.get("qa_completed") || "{}");\ncompleted[pm.info.requestName] = true;\npm.variables.set("qa_completed", JSON.stringify(completed));'
        events.append(event('test', HELPER + post))
    return {'name': name, 'request': r, 'event': events}

items = []
setup = []
for role, label in [('seller', '판매자'), ('bidder_a', '입찰자 A'), ('bidder_b', '입찰자 B')]:
    pre = ''
    if role == 'seller':
        pre = '''["seller", "bidder_a", "bidder_b"].forEach(r => {
  pm.variables.unset("qa_" + r + "_token");
  pm.variables.unset("qa_" + r + "_id");
});
pm.variables.unset("qa_product_created");
pm.variables.unset("qa_product_id");
'''
    pre += f'''if (!pm.variables.get("{role}_email") || !pm.variables.get("{role}_password")) {{
  pm.test("BLOCKED: {label} 계정 설정 필요", function () {{ throw new Error("Set collection Variables before running."); }});
  pm.execution.skipRequest();
}}
pm.variables.set("qa_login_payload", JSON.stringify({{
  email: pm.variables.get("{role}_email"), password: pm.variables.get("{role}_password")
}}));
'''
    post = f'''check("{label} 로그인 성공 및 세션 확인", function () {{
  pm.expect(pm.response.code).to.equal(200);
  const data = pm.response.json();
  pm.expect(data.access_token).to.be.a("string").and.not.empty;
  pm.expect(data.user.id).to.be.a("string").and.not.empty;
  pm.expect(data.user.email.toLowerCase()).to.equal(pm.variables.get("{role}_email").toLowerCase());
  pm.variables.set("qa_{role}_token", data.access_token);
  pm.variables.set("qa_{role}_id", data.user.id);
}});
'''
    if role == 'bidder_b':
        post += '''check("판매자와 입찰자 A/B는 서로 다른 계정", function () {
  const ids = ["seller", "bidder_a", "bidder_b"].map(r => pm.variables.get("qa_" + r + "_id"));
  pm.expect(ids.every(Boolean)).to.equal(true);
  pm.expect(new Set(ids).size).to.equal(3);
});'''
    login = request(label + ' 로그인', 'POST', '/auth/v1/token?grant_type=password',
        {'email': '{{'+role+'_email}}', 'password': '{{'+role+'_password}}'},
        role=None, guard=False, pre=pre, post=post)
    login['request']['body']['raw'] = '{{qa_login_payload}}'
    setup.append(login)
items.append({'name': '00 준비 - 계정 3개 로그인', 'item': setup,
              'description': '먼저 실행. 계정은 미리 가입하고 이메일 인증을 완료한 테스트 계정 3개 사용. 토큰은 실행 중 로컬 변수에만 저장.'})

CASES = [
    ('TC-BID-001', '정상 입찰', 'normal', 15000),
    ('TC-BID-002-EQUAL', '현재가와 같은 금액 거부', 'negative', 10000),
    ('TC-BID-002-LOWER', '현재가보다 낮은 금액 거부', 'negative', 9000),
    ('TC-BID-003', '두 사용자 순차 입찰', 'sequential', 20000),
    ('TC-CLOSE-001', '종료 후 입찰 차단', 'ended', 15000),
    ('TC-BID-004', '익명 입찰 차단', 'anonymous', 15000),
    ('TC-BID-005', '잘못된 토큰 입찰 차단', 'invalid', 15000),
    ('TC-BID-006', '다른 사용자 ID 위조 차단', 'forged', 15000),
    ('TC-BID-007', '금액 누락 입찰 거부', 'missing', None),
]

for case_id, label, mode, amount in CASES:
    pre = '''pm.variables.set("qa_case_failed", false);
pm.variables.set("qa_completed", "{}");
pm.variables.unset("qa_product_created");
pm.variables.unset("qa_product_id");
const ids = ["seller", "bidder_a", "bidder_b"].map(r => pm.variables.get("qa_" + r + "_id"));
const tokens = ["seller", "bidder_a", "bidder_b"].map(r => pm.variables.get("qa_" + r + "_token"));
if (!ids.every(Boolean) || !tokens.every(Boolean) || new Set(ids).size !== 3) {
  pm.variables.set("qa_case_failed", true);
  pm.test("BLOCKED: 계정 준비 실패", function () { throw new Error("Run 00 준비 first with 3 distinct accounts."); });
  pm.execution.skipRequest();
}
pm.variables.set("qa_title", "QA-POSTMAN-''' + case_id + '''-" + pm.variables.replaceIn("{{$guid}}"));
pm.variables.set("qa_end_time", new Date(Date.now() + 24 * 3600 * 1000).toISOString());
'''
    create_body = {'title': '{{qa_title}}', 'description': 'Postman 핵심 입찰 테스트 전용 상품',
                   'location': 'QA 테스트', 'category': '기타', 'starting_price': 10000,
                   'current_price': 10000, 'image_url': 'https://example.com/qa-test.jpg',
                   'end_time': '{{qa_end_time}}', 'seller_id': '{{qa_seller_id}}'}
    flow = [request('01 테스트 상품 생성', 'POST',
        '/rest/v1/products?select=id,title,seller_id,current_price,end_time', create_body,
        guard=False, pre=pre, post='''check("상품 생성 및 소유자 확인", function () {
  pm.expect(pm.response.code).to.equal(201);
  const data = rows(); pm.expect(data).to.have.lengthOf(1);
  const product = data[0];
  pm.expect(product.id).to.match(/^[0-9a-f-]{36}$/i);
  pm.expect(product.title).to.equal(pm.variables.get("qa_title"));
  pm.expect(product.seller_id).to.equal(pm.variables.get("qa_seller_id"));
  pm.variables.set("qa_product_id", product.id);
  pm.variables.set("qa_product_created", true);
  pm.expect(product.current_price).to.equal(10000);
  pm.expect(Date.parse(product.end_time)).to.be.above(Date.now());
});''')]
    if mode == 'ended':
        flow.append(request('02 종료 상태 준비', 'PATCH',
            '/rest/v1/products?id=eq.{{qa_product_id}}&seller_id=eq.{{qa_seller_id}}&select=id,end_time',
            {'end_time': '{{qa_past_time}}'}, pre='pm.variables.set("qa_past_time", new Date(Date.now() - 3600 * 1000).toISOString());',
            post='''check("경매 종료 시각 변경 확인", function () {
  pm.expect(pm.response.code).to.equal(200);
  const data = rows(); pm.expect(data).to.have.lengthOf(1);
  pm.expect(data[0].id).to.equal(pm.variables.get("qa_product_id"));
  pm.expect(Date.parse(data[0].end_time)).to.be.below(Date.now());
});'''))
    def bid_request(name, bid_amount, role='bidder_a', forged=False, rejection=None):
        body = {'product_id': '{{qa_product_id}}',
                'user_id': '{{qa_bidder_b_id}}' if forged else '{{qa_bidder_a_id}}',
                'bid_amount': bid_amount}
        if role == 'bidder_b': body['user_id'] = '{{qa_bidder_b_id}}'
        if bid_amount is None: body.pop('bid_amount')
        if rejection is None:
            post = '''check("입찰 성공: 금액·상품·사용자 일치", function () {
  pm.expect(pm.response.code).to.equal(201);
  const data = rows(); pm.expect(data).to.have.lengthOf(1);
  pm.expect(data[0].product_id).to.equal(pm.variables.get("qa_product_id"));
  pm.expect(data[0].user_id).to.equal(pm.variables.get("qa_''' + role + '''_id"));
  pm.expect(data[0].bid_amount).to.equal(''' + str(bid_amount) + ''');
});'''
        else:
            status, codes, message = rejection
            post = '''check("입찰 거부 및 오류 원인 확인", function () {
  pm.expect(pm.response.code).to.be.oneOf(''' + json.dumps(status) + ''');
  const error = pm.response.json();
  pm.expect(error).to.be.an("object");
'''
            if codes: post += '  pm.expect(error.code).to.be.oneOf(' + json.dumps(codes) + ');\n'
            if message: post += '  pm.expect(error.message).to.match(/' + message + '/i);\n'
            post += '});'
        return request(name, 'POST', '/rest/v1/bids?select=id,product_id,user_id,bid_amount', body, role=role, post=post)

    if mode in ('normal', 'sequential'):
        flow.append(bid_request('02 입찰자 A 정상 입찰', 15000))
        if mode == 'sequential':flow.append(bid_request('03 입찰자 B 더 높은 금액 입찰', 20000, role='bidder_b'))
    else:
        rejection = {
            'negative': ([400], ['P0001'], 'higher than current price'),
            'ended': ([400], ['P0001'], 'auction has ended|ended auction'),
            'anonymous': ([401,403], ['42501'], 'row.level security|permission'),
            'invalid': ([401], None, None),
            'forged': ([403], ['42501'], 'row.level security|permission'),
            'missing': ([400], ['23502'], 'bid_amount'),
        }[mode]
        flow.append(bid_request('03 검증 대상 입찰 요청', amount,
            role=None if mode=='anonymous' else 'invalid' if mode=='invalid' else 'bidder_a',
            forged=mode=='forged', rejection=rejection))

    expected = 20000 if mode=='sequential' else 15000 if mode=='normal' else 10000
    count = 2 if mode=='sequential' else 1 if mode=='normal' else 0
    flow.append(request('04 상품 재조회 - 현재가 검증', 'GET',
        '/rest/v1/products?id=eq.{{qa_product_id}}&select=id,title,current_price', role=None,
        post='''check("대상 상품 현재가 일치", function () {
  pm.expect(pm.response.code).to.equal(200);
  const data = rows(); pm.expect(data).to.have.lengthOf(1);
  pm.expect(data[0].id).to.equal(pm.variables.get("qa_product_id"));
  pm.expect(data[0].current_price).to.equal(''' + str(expected) + ''');
});'''))
    bids_post = '''check("입찰 내역 개수 및 저장 내용 확인", function () {
  pm.expect(pm.response.code).to.equal(200);
  const data = rows(); pm.expect(data).to.have.lengthOf(''' + str(count) + ''');
'''
    if count:
        bids_post += '''  pm.expect(data[0].product_id).to.equal(pm.variables.get("qa_product_id"));
  pm.expect(data[0].bid_amount).to.equal(''' + str(expected) + ''');
  pm.expect(data[0].user_id).to.equal(pm.variables.get("qa_''' + ('bidder_b' if mode=='sequential' else 'bidder_a') + '''_id"));
'''
        if count == 2:
            bids_post += '''  pm.expect(data[1].product_id).to.equal(pm.variables.get("qa_product_id"));
  pm.expect(data[1].bid_amount).to.equal(15000);
  pm.expect(data[1].user_id).to.equal(pm.variables.get("qa_bidder_a_id"));
'''
    bids_post += '});'
    flow.append(request('05 입찰 내역 재조회 - 생성 여부 검증', 'GET',
        '/rest/v1/bids?product_id=eq.{{qa_product_id}}&select=id,product_id,user_id,bid_amount&order=bid_amount.desc,created_at.asc',
        role=None, post=bids_post))
    flow.append(request('06 생성 상품 정리', 'DELETE',
        '/rest/v1/products?id=eq.{{qa_product_id}}&seller_id=eq.{{qa_seller_id}}&title=eq.{{qa_title}}',
        post='''check("상품 삭제 요청 성공", function () { pm.expect(pm.response.code).to.be.oneOf([200,204]); });'''))
    flow.append(request('07 삭제 결과 확인', 'GET',
        '/rest/v1/products?id=eq.{{qa_product_id}}&select=id', role=None,
        post='''check("생성 상품 삭제 확인", function () { pm.expect(pm.response.code).to.equal(200); pm.expect(rows()).to.have.lengthOf(0); });'''))
    required_steps = [step['name'] for step in flow]
    flow.append(request('08 입찰 내역 정리 및 TC 종합 판정', 'GET',
        '/rest/v1/bids?product_id=eq.{{qa_product_id}}&select=id', role=None,
        post='''check("관련 입찰 내역 삭제 확인", function () { pm.expect(pm.response.code).to.equal(200); pm.expect(rows()).to.have.lengthOf(0); });
check("''' + case_id + ''' 종합 판정: 준비·검증·정리 모두 성공", function () {
  const completed = JSON.parse(pm.variables.get("qa_completed") || "{}");
  const required = ''' + json.dumps(required_steps, ensure_ascii=False) + ''';
  pm.expect(required.every(name => completed[name] === true), "실행하지 않은 필수 요청이 있음").to.equal(true);
  pm.expect(pm.variables.get("qa_case_failed"), "앞 단계에서 실패한 검증이 있음").to.equal(false);
});
pm.variables.unset("qa_product_created");
pm.variables.unset("qa_product_id");'''))
    items.append({'name': case_id + ' ' + label, 'description':
        '사전 조건: 00 준비 완료, 서로 다른 계정 3개. 시작가 10000원의 신규 상품 사용. '
        '폴더 내 전체 요청을 순서대로 실행. 부분 실행/건너뜀은 TC PASS로 집계하지 않음. '
        '종료 상태 케이스는 과거 시각으로 변경하며 실제 경계 시각 대기 테스트가 아님.', 'item': flow})

variables = [
    {'key':'base_url','value':PUBLIC['base_url'],'type':'string'},
    {'key':'anon_key','value':PUBLIC['anon_key'],'type':'string'},
]
for role in ('seller','bidder_a','bidder_b'):
    for field in ('email','password'):
        variables.append({'key':role+'_'+field,'value':'','type':'string'})
collection = {
    'info': {'name':'Pa-Bi Core Bidding TC',
             'schema':'https://schema.getpostman.com/json/collection/v2.1.0/collection.json',
             'description':'핵심 8개 TC / 9개 입력 조건. 00 준비부터 Collection 전체를 Runner로 실행하세요. '
             'Variables의 계정 6개 값을 로컬에 입력하세요. 이메일 인증된 서로 다른 테스트 계정 3개가 필요합니다. '
             'QA-POSTMAN- 접두사의 상품을 생성·삭제합니다. 토큰·상품 ID는 실행 중 로컬 변수에만 보관합니다. '
             '실제 서버 결과 미실행. Python의 동시 입찰·연락처 권한 테스트 범위와 구분합니다.'},
    'auth': {'type':'noauth'}, 'variable': variables, 'item': items,
}
target=HERE/'pabi-core-bidding.postman_collection.json'
target.write_text(json.dumps(collection,ensure_ascii=False,indent=2)+'\n')
if __name__ == '__main__': print(target.name)
