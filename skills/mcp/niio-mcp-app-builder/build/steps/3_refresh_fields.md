# Step 3：重新整理欄位結構

先確認本次使用的部署環境，再取得其 API 基底網址、應用 ID、工作表 ID 與認證資訊。
API、MCP 與網站網址可能不同；不得由 MCP 網址自行推測，也不得跨環境共用 Token。

1. 從使用者選定的 MCP 連線讀取 `headers.Authorization`；若實際設定使用 URL 的 `Authorization` 參數，解碼後取值。保留完整認證字串，不假設固定前綴，不顯示 Token。
2. niio demo 的 API 基底網址預設為 `https://niiodemo.apsm.com.tw`。其他部署必須以 `--api-base` 指定該環境網址；不得將其他環境的憑證傳往 demo。網址必須包含 HTTPS，不能包含 `/mcp`、`/v3` 或驗證參數。
3. 執行下列腳本，將變數替換為此環境已確認的設定。範例變數必須先設定，不能直接照抄執行。

```bash
python3 {SKILL_DIR}/build/scripts/refresh_fields.py \
  --api-base "$NIIO_API_BASE" \
  --token "$NIIO_AUTHORIZATION" \
  {PROJECT_ROOT}/apps/{appName}/hap-context.json
```

腳本從 `hap-context.json` 讀取 `appId`、`worksheetIdByName`，以 GET 取得欄位結構並寫入 `worksheetContext.json`。
若網址、授權、回傳格式或任何工作表的欄位檢查失敗，停止本步驟並保留既有輸出，不得改用其他服務重試。

驗證：本次腳本成功結束；輸出的工作表數量等於已建立工作表數，每表的 `fields` 非空。
不寫 `progress`，由排程器統一管理。
