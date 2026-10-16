# 最小驗收包

預設離線、無憑證、無網路。Python 3.10+／Node 22；沒有額外執行依賴。

```powershell
foreach ($channel in 'api','cli','website','view') {
  python acceptance/check_capture.py --fixture --contract "acceptance/fixtures/$channel.contract.json" --capture acceptance/fixtures/capture.json
  if ($LASTEXITCODE) { throw "$channel 離線驗收失敗" }
}
node --test tests/test_website_gateway.mjs tests/test_view_acceptance.mjs
```

預期每個 channel 輸出 evidenceKind=mock、rows=1、remoteRequestPerformed=false；Node 測試涵蓋後端公開列與欄位投影、秘密隔離、錯誤及 SDK 目標限制。任何非零退出碼／非 JSON／目標不符／欄位多出或缺少／型別或筆數不符均失敗。不能把 fixture 檔當部署證據。

## 後續部署最小材料（未執行）

|通道|設定與可執行材料|預期與失敗判定|
|---|---|---|
|API|維護者提供完整確認過的唯讀 method/URL、非秘密 payload、憑證變數名稱；使用其確認的 HTTP 客戶端命令，停用自動轉址，最多 1 筆。不要由 MCP URL 拼接。保存去敏 capture，再執行下方驗證器|HTTP 200、JSON、業務 success 與已核准 rowsPath／目標／欄位符合。401/403/404 HTML、業務失敗或超時停止，不猜下一條路由|
|CLI|提供確切 hap 版本／既有 profile；先按版本 help 核對 accounts、whoami、worksheet record list 支援的語法，再以該 profile 對合成表限量唯讀。沒有已確認 flags 就不生成假命令|命令退出碼零且解析結果、部署與應用相符；自動更新、要求登入／切換或非 JSON 時停止。編輯器只驗 schema/inspect，不用修改來驗收|
|網站|現有 assets/server.config.mjs.template 和 server.mjs.template；後端設定 NIIO_API_BASE_URL、NIIO_AUTH_MODE，按模式提供 NIIO_AUTHORIZATION＋NIIO_APP_ID 或 NIIO_APP_KEY＋NIIO_APP_SIGN；已核准的 listPath／publishedField／fields|唯讀 GET 同源 /api/content/<已啟用資料集>；只公開發布列與白名單欄位，HTML/JS/網路請求不能出現秘密；未授權欄位或草稿出現即失敗|
|檢視外掛|在既有授權檢視使用 acceptance/view-readonly.mjs 的 readOne(api, config, expected)，expected 包含 appId/worksheetId/viewId；api 由已確認模板 SDK 提供|只呼叫一次 getFilterRows、pageSize=1，回傳陣列至多一筆；目標或 SDK 回應不符則拋錯。需另記實際檢視可開啟與主控台無錯誤，不以 mock 代替|

部署捕獲驗證：複製 fixture contract 為獨立檔，填實際已批准的 target、rowsPath、欄位及筆數，deploymentApproved=true；依契約保留去敏捕獲的 status/contentType/body/target，再執行：

```text
python acceptance/check_capture.py --contract <approved-contract.json> --capture <redacted-capture.json>
```

capture-contract-passed 只驗捕獲形狀，來源／時間／真實請求是否成功須人工核對。業務 success 必須在捕獲前核對，不可把錯誤包裝成 status=200 的假成功。完整原始證據由部署維護者受控保存，不寫入此公開儲存庫。

每筆去敏紀錄附：channel、工具／命令、版本、方法／端點（移除秘密查詢）、原參數結構（秘密值替換）、目標 ID、UTC 開始／結束時間、時區與精度、HTTP／退出碼、Content-Type、錯誤完整文字、request/correlation ID、業務狀態、預期與實際筆數、保存者。禁止 Authorization、cookie、token、AppKey/Sign 或個資列內容入版控。可用 ID 也按資料分類政策去敏；受控原件保留映射。

## CLI 編輯器 schema 離線驗收

在隔離目錄準備 Ajv 8.17.1（固定依賴 fast-deep-equal 3.1.3、fast-uri 3.1.0、json-schema-traverse 1.0.0、require-from-string 2.0.2），執行 `node acceptance/validate-editspec.cjs <ajv 套件絕對目錄>`，預期 schemas=10、offline-schema-passed。可加第二參數為合成 edit-spec JSON；先驗 envelope，再按 op.type 分派 module schema。任何不符退出 1；不呼叫 hap、不套用操作。這只驗本地 schema，不證明部署支援。
