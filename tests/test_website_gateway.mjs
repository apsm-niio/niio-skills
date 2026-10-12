import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import vm from 'node:vm';
const root = new URL('../skills/api/niio-api-website/', import.meta.url);
const source = await readFile(new URL('assets/server.mjs.template', root), 'utf8');
const { createHandler } = await import(`data:text/javascript;base64,${Buffer.from(source).toString('base64')}`);
const env = { NIIO_API_BASE_URL: 'https://deployment.example.test', NIIO_AUTH_MODE: 'bearer',
    NIIO_AUTHORIZATION: 'Bearer offline-secret', NIIO_APP_ID: 'app-test' };
const config = () => ({ datasets: { products: { enabled: true, public: true, restVerified: true,
    listPath: '/verified/rows/list', publishedField: 'published', publishedValue: '1',
    fields: { name: { id: 'title', type: 'text' }, image: { id: 'photo', type: 'image' } } } } });
const json = value => new Response(JSON.stringify(value), { headers: { 'Content-Type': 'application/json' } });
async function call(handler, url = '/api/content/products', method = 'GET') {
    const result = {};
    await handler({ url, method }, { writeHead(status, headers) { Object.assign(result, { status, headers }); },
        end(body) { result.body = body; result.data = JSON.parse(body); } });
    return result;
}

test('公開列與欄位投影；不洩漏草稿、成本、附件額外資訊、total 或秘密', async () => {
    let request;
    const handler = createHandler(config(), { env, fetchImpl: async (url, options) => {
        request = { url, options };
        return json({ success: true, data: { total: 999, rows: [
            { published: '1', title: '商品', cost: 900, photo: [{ downloadUrl: 'https://images.example.test/a.jpg', privateOwner: 'secret' }] },
            { published: '0', title: '草稿' }, { published: 1, title: '型別不符' }
        ] } });
    } });
    const result = await call(handler);
    assert.equal(result.status, 200);
    assert.deepEqual(result.data.data.rows, [{ name: '商品', image: 'https://images.example.test/a.jpg' }]);
    for (const forbidden of ['草稿', 'cost', 'privateOwner', '999', 'offline-secret']) assert.ok(!result.body.includes(forbidden));
    assert.equal(request.url, 'https://deployment.example.test/verified/rows/list');
    assert.equal(request.options.redirect, 'error');
    assert.equal(request.options.headers.Authorization, env.NIIO_AUTHORIZATION);
    assert.equal(request.options.headers['HAP-Appid'], 'app-test');
    assert.deepEqual(JSON.parse(request.options.body).filter.children[0].value, ['1']);
});

test('拒絕未知資料集、私有資料集、任意參數、重複頁碼及寫入方法，不呼叫上游', async () => {
    let count = 0;
    const handler = createHandler(config(), { env, fetchImpl: async () => { count++; } });
    for (const url of ['/api/content/internal', '/api/content/products?filter=x', '/api/content/products?fields=cost',
        '/api/content/products?url=https://other.test', '/api/content/products?page=1&page=2',
        '/api/content/products?limit=51', '/api/content/products?page=0', '/api/content/products/row-id']) {
        assert.ok((await call(handler, url)).status >= 400);
    }
    for (const method of ['POST', 'PUT', 'DELETE', 'PATCH']) assert.equal((await call(handler, undefined, method)).status, 405);
    assert.equal(count, 0);
    for (const change of [{ public: false }, { restVerified: false }, { publishedField: '' }, { listPath: '//other.test/x' }]) {
        const settings = config(); Object.assign(settings.datasets.products, change);
        assert.throws(() => createHandler(settings, { env }));
    }
    assert.throws(() => createHandler({ datasets: {} }, { env }));
});

test('失敗、HTML、重新導向、格式不符及過大回應只回傳一般錯誤', async () => {
    const responses = [
        () => new Response('offline-secret', { status: 404, headers: { 'Content-Type': 'text/html' } }),
        () => new Response('offline-secret', { headers: { 'Content-Type': 'text/html' } }),
        () => new Response('offline-secret', { status: 302, headers: { Location: 'https://other.test' } }),
        () => json({ success: false, error_msg: 'offline-secret' }),
        () => json({ success: true, data: {} }),
        () => new Response('x'.repeat(2 * 1024 * 1024 + 1), { headers: { 'Content-Type': 'application/json' } }),
        () => { throw new Error('offline-secret'); }
    ];
    for (const response of responses) {
        const result = await call(createHandler(config(), { env, fetchImpl: async () => response() }));
        assert.equal(result.status, 502); assert.ok(!result.body.includes('offline-secret'));
    }
});

test('Appkey 模式僅在後端產生協定標頭；錯誤部署設定拒絕啟動', async () => {
    let headers;
    const handler = createHandler(config(), { env: { NIIO_API_BASE_URL: env.NIIO_API_BASE_URL,
        NIIO_AUTH_MODE: 'appkey', NIIO_APP_KEY: 'key-test', NIIO_APP_SIGN: 'sign-test' },
        fetchImpl: async (_, options) => { headers = options.headers; return json({ success: true, data: { rows: [] } }); } });
    assert.equal((await call(handler)).status, 200);
    assert.equal(headers['HAP-Appkey'], 'key-test'); assert.equal(headers['HAP-Sign'], 'sign-test');
    assert.equal(headers.Authorization, undefined);
    for (const change of [{ NIIO_API_BASE_URL: 'http://other.test' }, { NIIO_API_BASE_URL: 'https://other.test/mcp' },
        { NIIO_API_BASE_URL: 'https://other.invalid' }, { NIIO_AUTH_MODE: '' }, { NIIO_AUTHORIZATION: '' }]) {
        assert.throws(() => createHandler(config(), { env: { ...env, ...change } }));
    }
});

test('瀏覽器模板只呼叫同源後端，不含秘密或任意路徑代理', async () => {
    const configSource = await readFile(new URL('assets/config.js.template', root), 'utf8');
    const apiSource = await readFile(new URL('assets/api.js.template', root), 'utf8');
    const mainSource = await readFile(new URL('assets/main.js.template', root), 'utf8');
    for (const source of [configSource, apiSource, mainSource]) {
        assert.doesNotMatch(source, /HAP_APPKEY|HAP_SIGN|HAP-Appkey|HAP-Sign|Authorization|NIIO_AUTHORIZATION/);
        new vm.Script(source);
    }
    let request;
    const context = vm.createContext({ fetch: async (url, options) => {
        request = { url, options }; return json({ success: true, data: { rows: [] } });
    } });
    vm.runInContext(configSource + '\n' + apiSource + '\nglobalThis.api = API;', context);
    await context.api.getRows('products');
    assert.equal(request.url, '/api/content/products?page=1&limit=20');
    assert.equal(request.options.credentials, 'same-origin');
    await assert.rejects(context.api.getRows('https://other.test'));
});
