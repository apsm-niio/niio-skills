# niio 部署驗證紀錄

日期：2026-10-07。此紀錄區分本機離線驗證與使用者回報的部署實測，不代表全部技能完成驗收。

| 項目 | 證據與狀態 | 後續驗收 |
|---|---|---|
| MCP 單表結構 | 使用者回報 `niio_personal_mcp.get_worksheet_structure` 成功取得「請購單」43 個欄位，含選項、關聯及來源欄位 | 已確認此工具可用；其他權限範圍須各自確認 |
| 原 REST 欄位路徑 | 使用者回報 demo 的 `/v3/app/worksheets/{id}` 回傳 404 HTML | 第 3 步已改用 MCP；此結果不證明其他 REST 路徑都不存在 |
| MCP 回應本機整理 | 兩表合成測試、下游填值模板、失敗保留舊檔及原子替換測試通過 | 在本機 Codex 用真實 MCP 完成兩張工作表的第 3 步，僅寫本機輸出 |
| 進度管理 | 排程指令及輸出契約已統一；由排程器驗證後推進，並行步驟等待匯合 | 在測試專案驗證成功恢復及失敗不推進 |
| 網站 API 技能 | `niio-api-website/assets/api.js.template` 仍呼叫 REST `/v3/.../rows/list` 等路徑 | 依部署文件確認 base、驗證、路由及瀏覽器 CORS，先做唯讀查詢；不能套用 MCP 成功結論 |
| API V3／檢視插件 | `niio-apiv3-data`、`niio-view-plugin/V3_API_INTEGRATION.md` 仍有 REST 範例 | 分別驗證讀取介面與插件執行環境；範例網域不是可用性保證 |
| CLI 建後精修 | Step 12 使用獨立 CLI 設定與登入 | 先核對部署主機、組織及應用，再唯讀對賬；不要只核對組織 ID 就認定環境相同 |
| 圖片／附件 | 126 張圖片已存入 repo，先前檔案完整性檢查通過；PDF／Word／Excel 未提供新的實際來源 | 測試環境實際載入圖片；其他必填附件仍需有效素材，不能使用佔位網址 |
| 完整建置 | 本次未建立、修改或發布 niio 應用 | 使用獨立測試應用驗證工作表、動作、檢視、範例資料、頁面、角色及工作流；發布與外部通知依實際授權執行 |

## 同步維護

- `localization/overrides/3_refresh_fields.md` 定義 MCP 取得回應流程。
- `localization/overrides/refresh_fields.py` 只做本機 JSON 驗證、整理與原子替換，不讀取憑證、不連線。
- `scripts/localize.py` 將這兩份內容套用至技能，並校正排程與輸出契約。被完整替換的兩個上游檔案以 SHA-256 固定，遇到變更先停止同步，審查後再更新對應規則。
- GitHub Action 在產生技能後執行 `tests/test_mcp_refresh.py`，通過後才提交。測試使用合成資料，不包含客戶資料或憑證。
- 不可把本機合成測試、Action 成功或單表 MCP 成功描述成完整建置已實測。
