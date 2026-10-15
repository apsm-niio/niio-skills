# Step 輸出契約

每一步回傳真實產物 ID、欲合併的資料、驗證結果及問題清單，由排程器合併至 context 或 plan；子代理不得直接寫入共用檔案。步驟沒有規劃項目時，附已核對方案的跳過理由。

排程器驗證本次產物後，透過 build_checkpoint.py finish 保存該步 done 與 evidence。Step 3 需有本次腳本結束碼 0、完整工作表 ID 集合與欄位數。Step 9 需驗證工作流 nodes；Step 10/11 需有發布證據；Step 12 需區分完成與待補。

成功依 buildState.steps[STEP].status=done 與證據判斷，不能只看 progress 是否改變：7、8、10 完成時 progress 可以保持原值，階段全部完成後才推進。下一步由 check 輸出的 nextSteps 決定，所有步驟序列執行。

失敗或工具逾時時保留 running 與最後成功 progress，停止派發；依 build/SKILL.md 唯讀核對，不自動重試。不可用舊檔存在或遠端請求已送出作為成功證據。

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
| 9 | 與 Step 7、8 匯合後寫入 `config_completed` | _(工作流設計寫入 niio-plan.json)_ |
| 10 | 與 Step 11 匯合後由排程器寫入 `workflows_deployed` | _(系統工作流 processId 已 publish)_ |
| 11 | 與 Step 10 匯合後由排程器寫入 `workflows_deployed` | `customActionWorkflows` |
| 12 | `completed` | _(CLI 回填結果或待補清單)_ |
