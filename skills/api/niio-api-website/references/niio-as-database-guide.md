# niio 網站架構與部署

## 資料流與公開範圍

瀏覽器呼叫網站自己的 `/api/content/products`；網站後端把秘密加到已確認的 niio REST 請求，再只回傳白名單欄位。此模板適合公開產品、新聞與案例；公開端點任何人都能讀，不是會員權限系統。

公開內容需同時滿足：資料集由管理者明確允許公開、REST 已唯讀驗證、資料列發布欄位符合設定值，以及欄位在白名單。後端送出固定篩選後，仍會再檢查每列發布值，避免上游未套用篩選而洩漏草稿。不回傳上游總筆數、系統欄位、未允許欄位或整個關聯／附件物件。

## 專案配置

```text
website/
  public/
    index.html
    js/config.js
    js/api.js
    js/main.js
  server.mjs
  server.config.mjs
  .env
  .gitignore
```

將 assets 的五個模板各自複製到對應位置並移除 `.template`。server 檔案及 `.env` 必須在 public 外；靜態伺服器不得以專案根目錄發布。將 `.env`、`.env.*` 納入專案的 `.gitignore`，僅允許無秘密的 `.env.example`。不要使用任何會進入前端 bundle 的環境變數前綴保存秘密。

最小 `public/index.html`：

```html
<!doctype html>
<html lang="zh-Hant">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>niio 產品展示</title></head>
<body>
  <p id="status" role="status"></p>
  <main id="products"></main>
  <script src="/js/config.js" defer></script>
  <script src="/js/api.js" defer></script>
  <script src="/js/main.js" defer></script>
</body>
</html>
```

依需求設計版面與樣式。預設文字透過 textContent 呈現，不把資料庫字串直接塞入 innerHTML；富文字若有需求，另採經審查的 HTML 清理策略。

## REST 位址與憑證

三種位址分開確認：網站 origin、MCP URL、REST origin。不可將 MCP 網址切掉 `/mcp` 後直接當成已驗證 API，也不能單憑 MCP 可用就認定其 Token 可用於 REST。

後端環境變數（只提供名稱與格式，不在文件或前端存真實憑證）：

| 變數 | 用途 |
|---|---|
| `NIIO_API_BASE_URL` | 已確認的 HTTPS origin，不含路徑、查詢或憑證 |
| `NIIO_AUTH_MODE` | 明確設為 `bearer` 或 `appkey` |
| `NIIO_AUTHORIZATION` | bearer 模式的完整 `Bearer …` 標頭，原樣使用 |
| `NIIO_APP_ID` | bearer 模式的應用 ID，送出標頭 `HAP-Appid` |
| `NIIO_APP_KEY`、`NIIO_APP_SIGN` | appkey 模式的後端憑證，送出原協定標頭 `HAP-Appkey`、`HAP-Sign` |
| `PORT` | 本機後端監聽連接埠，預設 3001 |

使用最小權限的 REST 憑證；不需要且不會讀取使用者本機 MCP 設定。REST 具體憑證適用性由部署端確認，不能自動互換驗證模式。

在 Node.js 22 以上環境啟動（`.env` 由管理者以安全方式建立，不提交 git）：

```bash
node --env-file=.env server.mjs
```

服務預設只監聽 `127.0.0.1`。由網站伺服器將同源 `/api/content/` 反向代理至後端，網站靜態根目錄設定為 public。後端不提供靜態檔案，也不啟用跨來源 CORS。依部署補上 HTTPS、請求速率限制與監控；模板限制每頁 50 筆、最多 8 個同時上游請求、10 秒逾時及 2 MiB 上游回應。

## 設定一組公開資料

先用 MCP 取得真實欄位 ID，再驗證該部署 REST 的列表路徑與 payload。`server.config.mjs` 中 products 起初停用，路徑與欄位皆為空值，不能不經設定就上線。

1. 在 listPath 填入已驗證的固定路徑，例如由部署文件取得的 `/v3/app/worksheets/{實際ID}/rows/list`；這只是形狀範例，不代表所有 niio 部署都提供此路由。
2. 填 publishedField 與 publishedValue。型別須與實測一致：字串 `'1'`、數字 `1`、布林 `true` 不相等。
3. 填 fields；鍵為前端公開別名，如 name、description、price、image，值指定真實欄位 ID 及輸出型別。
4. 只允許 text／number／boolean／image。型別不符輸出 null；number 不會默默把字串轉數字。image 只回傳 HTTPS URL，若來源為附件陣列則取第一項 downloadUrl；不要公開含私人授權或不適合公開的簽名網址。
5. 排序只在後端 sorts 設定，瀏覽器不可自訂。
6. 驗證列表資料、發布篩選與公開範圍後，明確設定 public、restVerified、enabled 為 true。

模板發送固定 POST 列表讀取請求，body 包含 pageIndex、pageSize、useFieldIdAsKey、fields、sorts 與 filter。filter 使用 group／AND／condition／eq／value 陣列。若部署的語法或回應格式不同，需先修正後端 adapter 並以唯讀方式驗證；不能只把 restVerified 改成 true。

回應必須為 HTTP 成功、JSON Content-Type、success: true、data.rows 陣列。404 HTML、重新導向、驗證失敗或格式不符時，前端只收到一般錯誤訊息，不能收到上游本文、Token、完整設定或錯誤堆疊。

## 前端與擴充

前端呼叫 `API.getRows('products', { pageIndex: 1, pageSize: 20 })`。後端只接受 GET 以及 page、limit；工作表、filter、fields、sorts、URL 及 rowId 不能由客戶端指定。

新增 news 或 cases：在後端另設一組獨立資料集與發布條件，前端 CONFIG.DATASETS 增加對應名稱，並按其公開欄位繪製畫面。不要複用 products 的工作表／發布欄位。

需要內容詳情時，另設固定、受白名單限制的詳情路由，仍必須檢查發布／授權條件；模板不提供任意 rowId 讀取。會員與內部資料必須另外驗證工作階段、租戶與資料列權限。表單寫入還需輸入白名單、長度與型別限制、防濫用與適用的 CSRF 保護，不能直接開放通用 niio 寫入代理。

## 驗收與舊專案遷移

- 確認瀏覽器下載的 JS、HTML、source map 與網路請求不含 niio 秘密。
- 確認未發布列、未允許欄位、額外附件資訊不回傳；不能只依賴前端隱藏。
- 確認偽造 filter／worksheetId／URL、未知資料集與 POST／DELETE 等寫入方法被拒絕。
- 模擬 JSON 失敗、HTML、重新導向與逾時，前端不得收到上游錯誤本文。
- 再對實際部署做已授權的唯讀測試，分開記錄本機測試與部署測試結果。

舊版 config.js／api.js／main.js 必須整組遷移，不與本模板混用。若真實憑證曾發布到前端，移除後仍需由管理者撤銷或輪替該憑證；只刪除目前檔案不能收回已被下載的秘密。本次模板修正不代表任何既有網站已遷移。
