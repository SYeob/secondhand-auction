// Offline contract checks for generated Postman scripts. No network or credentials.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { randomUUID } = require('node:crypto');
const collection = JSON.parse(fs.readFileSync(path.join(__dirname, 'pabi-core-bidding.postman_collection.json')));

function expect(value) {
  let negate = false;
  let chain;
  const verify = (ok, message) => { assert.ok(negate ? !ok : ok, message); negate = false; return chain; };
  const methods = {
    equal: other => verify(value === other, `${JSON.stringify(value)} != ${JSON.stringify(other)}`),
    oneOf: others => verify(others.includes(value), 'Unexpected value'),
    a: type => verify(type === 'array' ? Array.isArray(value) : typeof value === type, 'Wrong type'),
    an: type => methods.a(type),
    match: pattern => verify(typeof value === 'string' && pattern.test(value), 'Pattern mismatch'),
    lengthOf: length => verify(value.length === length, 'Wrong length'),
    above: other => verify(value > other, 'Not above'),
    below: other => verify(value < other, 'Not below'),
  };
  chain = new Proxy({}, { get(_target, key) {
    if (['to', 'be', 'have', 'and'].includes(key)) return chain;
    if (key === 'not') { negate = !negate; return chain; }
    if (key === 'empty') return verify(value == null || value.length === 0, 'Unexpected emptiness');
    if (key in methods) return methods[key];
    throw new Error('Unsupported assertion: ' + String(key));
  }});
  return chain;
}

function run(options = {}) {
  const values = new Map(collection.variable.map(v => [v.key, v.value]));
  for (const role of ['seller', 'bidder_a', 'bidder_b']) {
    values.set(role + '_email', options.noCredentials ? '' : role + '@test.invalid');
    values.set(role + '_password', options.noCredentials ? '' : 'offline-"quoted"-\\password');
  }
  const ids = { seller: randomUUID(), bidder_a: randomUUID(), bidder_b: randomUUID() };
  if (options.sameAccount) ids.bidder_b = ids.bidder_a;
  const products = new Map(); const bids = [];
  const tests = []; let networkCalls = 0; let creates = 0;
  const resolve = text => String(text).replace(/\{\{([^}]+)\}\}/g, (_m, key) => key === '$guid' ? randomUUID() : String(values.get(key) ?? ''));
  const error = (status, code, message) => ({ status, data: { code, message } });
  function server(req) {
    networkCalls++;
    const url = new URL(resolve(req.url));
    const body = req.body ? JSON.parse(resolve(req.body.raw)) : {};
    const headers = Object.fromEntries(req.header.map(h => [h.key, resolve(h.value)]));
    const role = headers.Authorization?.replace('Bearer offline-token-', '');
    if (url.pathname === '/auth/v1/token') {
      const user = body.email.split('@')[0];
      assert.equal(body.password, values.get(user + '_password'), 'Password must survive JSON encoding');
      return { status: 200, data: { access_token: 'offline-token-' + user, user: { id: ids[user], email: body.email } } };
    }
    const productId = url.searchParams.get('id')?.replace(/^eq\./, '');
    if (url.pathname.endsWith('/products')) {
      if (req.method === 'POST') {
        assert.equal(role, 'seller');
        const id = randomUUID(); const product = { id, ...body }; products.set(id, product); creates++;
        return { status: 201, data: [product] };
      }
      const product = products.get(productId);
      if (req.method === 'PATCH') {
        assert.equal(role, 'seller');
        if (product) Object.assign(product, body);
        return { status: 200, data: product ? [product] : [] };
      }
      if (req.method === 'DELETE') {
        assert.equal(role, 'seller');
        assert.equal(url.searchParams.get('seller_id'), 'eq.' + ids.seller);
        assert.equal(url.searchParams.get('title'), 'eq.' + product.title);
        if (!options.noDelete) {
          products.delete(productId);
          for (let i = bids.length - 1; i >= 0; i--) if (bids[i].product_id === productId) bids.splice(i, 1);
        }
        return { status: 204, data: null };
      }
      return { status: 200, data: product ? [product] : [] };
    }
    if (url.pathname.endsWith('/bids')) {
      if (req.method === 'GET') {
        const id = url.searchParams.get('product_id').replace(/^eq\./, '');
        return { status: 200, data: bids.filter(b => b.product_id === id).sort((a,b) => b.bid_amount-a.bid_amount) };
      }
      if (headers.Authorization === 'Bearer invalid.test.token') return error(401, 'PGRST301', 'Invalid JWT');
      if (!headers.Authorization) return error(401, '42501', 'new row violates row-level security policy');
      if (body.user_id !== ids[role]) return error(403, '42501', 'new row violates row-level security policy');
      const product = products.get(body.product_id);
      if (Date.parse(product.end_time) <= Date.now()) return error(400, 'P0001', 'Auction has ended');
      if (!Object.hasOwn(body, 'bid_amount')) return error(400, '23502', 'null value in column bid_amount');
      if (body.bid_amount <= product.current_price && !options.acceptLower) {
        return error(400, 'P0001', options.wrongBusinessError ? 'Unrelated database exception' : 'Bid amount must be higher than current price');
      }
      const bid = { id: randomUUID(), ...body }; bids.push(bid); product.current_price = body.bid_amount;
      return { status: 201, data: [bid] };
    }
    throw new Error('Unknown route');
  }
  const skipSignal = Symbol('skip');
  for (const folder of collection.item) {
    for (const item of folder.item) {
      if (options.skipValidation && folder.name.startsWith('TC-BID-001') &&
          /입찰자 A 정상 입찰|상품 재조회|입찰 내역 재조회/.test(item.name)) continue;
      let response;
      const pm = {
        info: { requestName: item.name },
        variables: { get:k=>values.get(k), set:(k,v)=>values.set(k,v), unset:k=>values.delete(k), replaceIn:resolve },
        expect,
        test(name, fn) { try { fn(); tests.push({ folder:folder.name, name, passed:true }); }
          catch(error) { tests.push({ folder:folder.name, name, passed:false, error:error.message }); } },
        execution: { skipRequest() { throw skipSignal; } },
      };
      try {
        for (const e of item.event.filter(e=>e.listen==='prerequest')) vm.runInNewContext(e.script.exec.join('\n'), { pm, Date, Set });
        response = server(item.request);
        pm.response = { code:response.status, json:()=>JSON.parse(JSON.stringify(response.data)) };
        for (const e of item.event.filter(e=>e.listen==='test')) vm.runInNewContext(e.script.exec.join('\n'), { pm, Date, Set });
      } catch(error) {
        if (error !== skipSignal) {
          values.set('qa_case_failed', true);
          tests.push({ folder:folder.name, name:'script/runtime', passed:false, error:error.message });
        }
      }
    }
  }
  return { tests, finals:tests.filter(t=>t.name.includes('종합 판정')), networkCalls, creates, remaining:products.size };
}

// Parse every script before evaluating scenarios, including paths not reached in a run.
let requestCount = 0;
for (const folder of collection.item) for (const item of folder.item) {
  requestCount++;
  assert.equal(item.request.auth.type, 'noauth');
  for (const event of item.event) new vm.Script(event.script.exec.join('\n'));
}
assert.equal(collection.item.length - 1, 9);
for (const role of ['seller','bidder_a','bidder_b']) {
  for (const field of ['email','password']) assert.equal(collection.variable.find(v=>v.key===role+'_'+field).value, '');
}
const good = run();
assert.deepEqual(good.tests.filter(t=>!t.passed), []);
assert.equal(good.finals.length, 9);
assert.equal(good.remaining, 0);
assert.equal(good.creates, 9);
for (const option of ['acceptLower','wrongBusinessError','noDelete','skipValidation']) {
  const result = run({ [option]:true });
  assert.ok(result.tests.some(t=>!t.passed), option+' must fail');
  assert.ok(result.finals.some(t=>!t.passed), option+' must fail overall TC');
  if (option !== 'noDelete') assert.equal(result.remaining, 0, option+' still cleans up');
}
for (const option of ['noCredentials','sameAccount']) {
  const result = run({ [option]:true });
  assert.equal(result.creates, 0, option+' must not create products');
  assert.equal(result.finals.length, 0, option+' cannot report TC PASS');
  assert.ok(result.tests.some(t=>!t.passed));
}
console.log(JSON.stringify({ requestCount, datasets:9, tcCount:8, goodRunAssertions:good.tests.length,
  checks:['happy path','accepted forbidden bid','unrelated 400 error','delete no-op','skipped steps','missing credentials','duplicate users'],
  liveServerExecuted:false }, null, 2));
