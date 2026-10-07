# Step 輸出契約

每個 step 執行完成後，無論是 subagent 模式還是內聯模式，都必須產出以下標準化結果。

## 輸出結構

各 step 回傳成功或失敗證據；只有排程器可在驗證完成後更新 `hap-context.json` 的 progress。並行步驟必須等待匯合，依 `PROGRESS.md` 與 `build/SKILL.md` 路由推進。

### 成功

1. 提交本次成功證據，由排程器依 `PROGRESS.md` 驗證後更新進度；Step 3 必須包含本次腳本結束碼 0、完整工作表 ID 集合及欄位數，不能僅檢查舊檔存在。
2. 寫入該步驟負責的 ID 對映欄位（見 `CONTEXT.md`）
3. 透過 ⛔ 驗證斷言

### 失敗

1. **不更新** `progress` 欄位（保持前一步的狀態值）
2. 排程器發現 progress 未推進 → 判定為失敗 → 向使用者報告錯誤

## 排程器驗證方法

排程器先驗證本次步驟產出，在並行匯合條件滿足後才寫入進度，再讀回 `hap-context.json` 檢查：

```
if context.progress == 目前步驟的預期完成狀態:
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
| 6 | 與 Step 5 均完成後寫入 `sample_data_created` | _(無新欄位，資料直接寫入平台)_ |
| 5b | `page_shells_created` | `customPageIdByName`, `chatbotIdByName`（若有） |
| 7 | 與 Step 8、9 匯合後寫入 `config_completed` | `customPageIdByName`, `chatbotIdByName`（若有） |
| 8 | 與 Step 7、9 匯合後寫入 `config_completed` | `roleContext` |
| 9 | 與 Step 7、8 匯合後寫入 `config_completed` | _(工作流設計寫入 hap-plan.json)_ |
| 10 | 與 Step 11 匯合後由排程器寫入 `workflows_deployed` | _(系統工作流 processId 已 publish)_ |
| 11 | 與 Step 10 匯合後由排程器寫入 `workflows_deployed` | `customActionWorkflows` |
| 12 | `completed` | _(CLI 回填結果或待補清單)_ |
