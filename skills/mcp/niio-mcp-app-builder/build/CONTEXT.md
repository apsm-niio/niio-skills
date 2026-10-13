# niio-context.json 結構定義

本檔案定義 `{PROJECT_ROOT}/apps/{appName}/niio-context.json` 的完整結構。所有步驟讀寫 context 時必須遵守此 schema。

## 結構

```json
{
  "appId": "string",
  "appName": "string",
  "org_id": "string",
  "progress": "string (見 PROGRESS.md)",

  "cliAvailable": "boolean (CLI 自檢寫入：本機 niio CLI 是否已安裝且已登入；未登入會在自檢階段自動瀏覽器登入。組織校正與設目前應用由 Step 12 處理)",

  "sectionIdByName": {
    "分組名稱": "sectionId"
  },
  "worksheetIdByName": {
    "工作表名稱": "worksheetId"
  },
  "actionIdByName": {
    "動作名稱": "actionId"
  },
  "viewIdByName": {
    "工作表名稱-檢視名稱": "viewId"
  },
  "customPageIdByName": {
    "頁面名稱": "pageId"
  },
  "chatbotIdByName": {
    "助手名稱": "chatbotId"
  },
  "roleContext": [
    {
      "roleId": "string",
      "roleName": "string"
    }
  ],
  "customActionWorkflows": [
    {
      "actionName": "string",
      "processId": "string",
      "published": true
    }
  ]
}
```

## 寫入規則

- **每個步驟只寫入自己負責的欄位**，不修改其他步驟的欄位
- **只存 ID 對映**，不存 MCP 原始回傳的完整物件
- `progress` 欄位由每步完成時更新，值域見 `PROGRESS.md`
- 欄位結構（fields）儲存在獨立檔案 `worksheetContext.json`，不寫入 `niio-context.json`，避免上下文膨脹

## worksheetContext.json 使用契約

`worksheetContext.json` 由 Step 3 寫入，**Step 4~10 只讀**。

- Step 4~10 中需要的欄位 ID、選項 key 等，**必須且只能從 `worksheetContext.json` 查詢，嚴禁重複呼叫 `get_worksheet_structure`**
- 檢視 ID 從 `viewIdByName`（儲存在 `niio-context.json`）中取得
- 該檔案在 Step 3 寫入後**不再修改**


## 填值模板中繼資訊契約

先重新執行 Step 3，保留 MCP 回傳的 isTitle、isReadOnly、required、subType（缺少時保持缺少，不補猜值）。generate_fill_templates.py 僅以明確 isTitle=true 識別標題，包含非文字與唯讀標題，完整標題資訊在 titleFields；不得猜第一個 Text。只把明確 isReadOnly=false 且非系統／計算型別的欄位列入填值候選，Rollup 不可填寫。Relation 的空 alias 不代表唯讀，fieldKey 可使用 id；關聯來源與設定保留。

檢查 excludedFields、metadataIssues 與 requiresReview。舊 worksheetContext 缺少中繼資訊時，須從原始 MCP 回應重新整理；不能以模板生成成功認定可寫入。requiresReview=true 時停止自動填值並確認問題。relationDeps 只代表候選可填關聯的依賴，不代表完整結構關聯。required 與 subType 僅保留原值，填值前仍需按真實欄位型別、必填與權限驗證。此腳本不保證伺服器端寫入權限，也不會發出寫入請求。
