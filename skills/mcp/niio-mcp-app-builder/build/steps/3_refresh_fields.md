# Step 3：透過 MCP 重新整理欄位結構

沿用排程器已選定且連線成功的 niio MCP 服務。由 AI 呼叫工具、保存回應及執行本機整理；MCP 不會自行執行整份建置流程。
應用與工作表 ID 從 `hap-context.json` 的 `appId`、`worksheetIdByName` 取得，無需使用者重填。
本步不讀取或要求 REST Token、AppKey、Sign、API 基底網址，也不呼叫 REST、CLI 或其他環境作為備援。

## 執行流程

1. 讀取並驗證 context：`appId` 非空、`worksheetIdByName` 非空且 ID 不重複。沿用目前部署與 MCP 服務；恢復既有專案時若無法確認屬於同一環境，先停止並確認。
2. 檢查所選 MCP 的 `get_worksheet_structure` 工具及實際參數結構，使用工具宣告的應用 ID、工作表 ID 參數並選擇 JSON 格式（若工具提供 format 參數則使用 `json`）。不得猜測參數名稱或改選另一個服務。
3. 在應用專案目錄下建立本次專用的暫存資料夾，記為 `MCP_RESPONSE_DIR`。每張工作表呼叫一次工具，取得完整的業務 JSON 回應。若工具以文字內容包住 JSON，解析該 JSON；若提供結構化回應，取其業務物件。遇到錯誤、截斷或不完整回應，停止，不補造欄位、不沿用上次暫存檔。
4. 驗證 `success: true`、非空 `data.fields[]`，每個欄位必須有 `id`、`name` 與文字型別 `type`。保留 `alias`、`options`（含 key/value/index/isDelete）、`dataSource`、`sourceField`、`relation`。若回應包含工作表 ID，須與請求一致。
5. 將每張工作表的完整回應存成 `{MCP_RESPONSE_DIR}/{worksheetId}.json`，外層格式如下。外層 ID 使用本次工具呼叫的 ID；`response` 必須來自工具，不可自行產生成功回應。不得加入憑證或完整 MCP 連線 URL。

```json
{
  "appId": "本次應用ID",
  "worksheetId": "本次工作表ID",
  "response": {"success": true, "data": {"fields": []}}
}
```

上例只表示封裝結構，空 fields 不能通過驗證。完整回應僅存放於本次暫存檔，不寫進 `hap-context.json` 或提交到版本控制。

6. 全部取得後，執行本機整理命令（變數由 AI 設定，不要求使用者手動輸入）：

```bash
python3 "{SKILL_DIR}/build/scripts/refresh_fields.py" \
  --responses-dir "{MCP_RESPONSE_DIR}" \
  "{PROJECT_ROOT}/apps/{appName}/hap-context.json"
```

腳本只讀取本機 JSON，不發出網路請求；全部驗證成功後，以原子替換寫入同目錄的 `worksheetContext.json`。
保留原輸出結構 `[{worksheetId, worksheetName, fields}]`，排除已刪除選項，保留後續填值、檢視與工作流所需資訊。
任何工作表失敗都不替換舊檔，也不推進進度；不可因舊檔存在就判定成功。

7. 檢查命令本次結束碼為 0、工作表 ID 集合與 context 完全一致、各表欄位數與本次 MCP 回應一致。清理本次暫存資料夾，僅刪除此步建立的暫存檔。
8. 本步不寫 `progress`；排程器驗證成功後才寫入 `progress=fields_refreshed`。下游依舊讀取 `worksheetContext.json`。

## 停止條件

缺少工具、工具拒絕存取、回應不完整、欄位型別不是預期文字型別或本機驗證失敗時，回報工作表與失敗原因，保留舊輸出與進度。工具不存在時請管理者確認部署能力，不引導使用者反覆找 REST 憑證。
