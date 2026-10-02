# Step 輸出契約

每個 step 執行完成後，無論是 subagent 模式還是內聯模式，都必須產出以下標準化結果。

## 輸出結構

每步完成時，透過更新 `hap-context.json` 來表達結果：

### 成功

1. 將 `progress` 欄位更新為當前步驟對應的完成狀態（見 `PROGRESS.md`）
2. 寫入該步驟負責的 ID 對映欄位（見 `CONTEXT.md`）
3. 透過 ⛔ 驗證斷言

### 失敗

1. **不更新** `progress` 欄位（保持前一步的狀態值）
2. 排程器發現 progress 未推進 → 判定為失敗 → 向使用者報告錯誤

## 排程器驗證方法

排程器在每步完成後，讀取 `hap-context.json` 檢查：

```
if context.progress == 當前步驟的預期完成狀態:
    ✅ 步驟成功，繼續下一步
else:
    ❌ 步驟失敗，報告錯誤並停止
```

## 各步驟的預期產出

| Step | 預期 progress | 必須寫入的欄位 |
|------|--------------|---------------|
| 1 | `app_created` | `appId`, `sectionIdByName` |
| 2 | `worksheets_created` | `worksheetIdByName` |
| 3 | `fields_refreshed` | _(寫入 worksheetContext.json)_ |
| 4 | `actions_created` | `actionIdByName` |
| 5 | `views_created` | `viewIdByName` |
| 6 | `sample_data_created` | _(無新欄位，資料直接寫入平台)_ |
| 7 | `pages_created` | `customPageIdByName`, `chatbotIdByName`（若有） |
| 8 | `roles_created` | `roleContext` |
| 9 | `workflows_designed` | _(工作流設計寫入 hap-plan.json)_ |
| 10 | `system_workflows_published` | _(系統工作流 processId 已 publish)_ |
| 11 | `completed` | `customActionWorkflows` |
