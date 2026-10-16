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

## 基本檢視與瀏覽器驗收證據

Step 5 證據需按交付目標表記錄 worksheetId、實際 viewId、歸屬核對與缺少項目；無檢視的瀏覽器目標表不得以「plan 無規劃」跳過。僅 MCP 資料測試的範圍例外須明確記錄，不能等同瀏覽器交付。

最終報告分列：

| 項目 | 證據與結果 |
|---|---|
| MCP 結構／資料 | 已讀回的 ID、數量及核對結果 |
| 檢視 | 每張目標表的 viewId 與歸屬 |
| 瀏覽器存取 | 目標使用者、確認時間、通過／失敗／待驗證；標示使用者回報或工具實測 |
| 畫面／品牌 | 僅報告實際檢查範圍；能看到資料不等於全畫面驗收 |

不得從檢視存在推定權限足夠，也不得從權限原始值推定瀏覽器必定失敗。遇到缺口先唯讀診斷，只修正已授權的最小範圍，不開放所有人權限。


## 自訂動作與角色的驗收證據

Step 11 的 done 僅代表節點與發布核對完成，不代表功能驗收通過；即使 progress=completed，也必須保留以下未驗證項目，不得宣稱全面驗收完成。

| 項目 | 必要證據 |
|---|---|
| 工作流設定 | appId、worksheetId、actionId、processId、發布版本及綁定核對；不可讀項目列缺口 |
| 指定入口實測 | 按鈕或其他已核實入口、測試紀錄 ID、操作時間與時區、操作者、操作前後值；來源為工具實測或使用者回報 |
| 防重複 | 分列介面禁止重點、後端條件防護、實際重複請求驗證；按鈕停用不代表後兩者通過 |
| 角色有效權限 | 每個測試角色及帳號的允許／禁止操作；空成員角色或管理員成功不能作為一般成員通過證據 |
| 未解問題 | 工具錯誤、結果不明、未測項目、可繼續項目及下一步；不得用另一入口成功結清原工具錯誤 |

沒有角色測試帳號時保留「待驗證：缺少測試帳號」，可繼續其他已授權項目，不自行授權或要求無限重測。所有驗收項目使用通過／失敗／待驗證／受阻，附證據來源；未取得執行紀錄不能推論請求未被接收。
