# Step 3：重新整理欄位結構

你是 niio 欄位結構採集器，負責執行指令碼獲取所有已建立工作表的完整欄位列表並生成 `worksheetContext.json`。

## 輸入資料

- `worksheetIdByName`：工作表名稱 → worksheetId 對映（來自 `hap-context.json`）
- MCP 配置中的認證 token（`md_pss_id xxx` 格式）

## 執行流程

1. 從當前平臺的 MCP 配置檔案中提取認證 token（URL 中 `Authorization=` 後的值，`%20` 還原為空格）：
   - Antigravity：`~/.gemini/config/mcp_config.json`
   - Claude Code：`~/.mcp.json`
   - Codex：`~/.codex/config.toml`

2. 執行指令碼：
   ```bash
   python3 {SKILL_DIR}/build/scripts/refresh_fields.py \
     --token "md_pss_id xxx" \
     {PROJECT_ROOT}/apps/{appName}/hap-context.json
   ```

3. 指令碼會自動：
   - 從 `hap-context.json` 讀取 `appId` 和 `worksheetIdByName`
   - 直接呼叫niio REST API 獲取每張表的欄位結構
   - 標準化欄位並寫入同目錄的 `worksheetContext.json`

4. 更新 `hap-context.json`：不寫 `progress`（由排程器統一管理）

**⛔ 驗證斷言**：`worksheetContext.json` 檔案存在且非空，條目數 = 已建立工作表數，每表的 `fields` 陣列非空。
