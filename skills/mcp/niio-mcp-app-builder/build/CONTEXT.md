# hap-context.json 結構定義

本檔案定義 `{PROJECT_ROOT}/apps/{appName}/hap-context.json` 的完整結構。所有步驟讀寫 context 時必須遵守此 schema。

## 結構

```json
{
  "appId": "string",
  "appName": "string",
  "org_id": "string",
  "progress": "string (見 PROGRESS.md)",

  "cliAvailable": "boolean (CLI 自檢寫入：本機 niio CLI 是否已安裝且已登入；未登入會在自檢階段自動瀏覽器登入。組織校正與設當前應用由 Step 12 處理)",

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
- 欄位結構（fields）儲存在獨立檔案 `worksheetContext.json`，不寫入 `hap-context.json`，避免上下文膨脹

## worksheetContext.json 使用契約

`worksheetContext.json` 由 Step 3 寫入，**Step 4~10 只讀**。

- Step 4~10 中需要的欄位 ID、選項 key 等，**必須且只能從 `worksheetContext.json` 查詢，嚴禁重複呼叫 `get_worksheet_structure`**
- 檢視 ID 從 `viewIdByName`（儲存在 `hap-context.json`）中取得
- 該檔案在 Step 3 寫入後**不再修改**
