# Step 5b：建立自訂頁面空殼與 AI 助手

你負責為所有自訂頁面建立空白導航項，並建立所有 AI 助手。本步驟只建立物件、取得 ID，**不設定頁面元件內容**（元件設定由 Step 7 完成）。

## 輸入資料

- `appId`：應用 ID
- `sectionIdByName`：導航分組名稱 → sectionId 對映（來自 `hap-context.json`）
- `customPages`：頁面規劃清單（來自 `hap-plan.json`）
- `aiAssistants`：AI 助手規劃清單（來自 `hap-plan.json`，可能為空陣列）

## 執行流程

### 階段 A：建立自訂頁面空殼

對每個自訂頁面，呼叫 `create_app_items` 建立空白自訂頁面項（掛在指定導航分組下），獲得頁面 ID：
- `icon`：根據 `pageType` 設定——`dashboard` 傳 `"sys_control-panel_traffic"`，`workspace` 傳 `"2_3_statistics"`

記錄 `customPageIdByName`（格式：`"頁面名稱" → pageId`）。

**⛔ 驗證斷言**：`customPageIdByName` 條目數 = plan 中自訂頁面數量。

### 階段 B：建立 AI 助手

1. 讀取 `hap-plan.json` 中的 `aiAssistants` 陣列
   - 若為空陣列或不存在 → 跳過此階段
2. 對每個 AI 助手，呼叫 `create_chatbot` 建立：
   - 必填參數：`appId`、`name`、`prompt`、`welcomeMessage`、`presetQuestions`
   - `prompt`：基於助手描述生成簡練的系統提示詞
   - `presetQuestions`：根據業務場景生成高頻預設問題，**必須少於 5 個**
   - `icon`：固定使用 `17_6_reddit`
   - `sectionId`：從 `sectionIdByName` 查詢所在導航分組 ID
3. 記錄 `chatbotIdByName`（格式：`"助手名稱" → chatbotId`）

**⛔ 驗證斷言**：若 plan 有 AI 助手，則 `chatbotIdByName` 條目數匹配。若 plan 無 AI 助手，直接跳過。

### 完成

更新 `hap-context.json`：寫入 `customPageIdByName` 和 `chatbotIdByName`（若有）。不寫 `progress`（由排程器統一管理）。
