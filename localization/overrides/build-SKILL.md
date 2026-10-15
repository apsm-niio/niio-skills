---
name: build
description: niio 應用建置排程器，以持久檢查點逐步建置與安全續跑。
---

# niio 應用建置排程器

先讀取 niio-plan.json 與 CONTEXT.md、OUTPUT_CONTRACT.md。首次寫入及恢復前先執行根 scripts/project_files.py 的 check／migrate，按根技能處理檔名衝突。所有工具使用已選定的 niio MCP；本機腳本不代替遠端驗證。

## 持久檢查點與續跑

檢查點位於 niio-context.json 的 buildState；progress 由 build_checkpoint.py 同一筆原子更新。只有排程器寫 context 與 plan；步驟執行器回傳變更，由排程器合併，禁止子代理直接覆蓋共用檔案。若個別 steps 檔案要求直接寫入共用檔案或 progress，以本節為準，改為回傳變更供排程器合併；合併採暫存檔加原子取代，保留所有既有檢查點。

目前採序列執行（包含原本並行的 4/6、7/8/9、10/11），以確保恢復時能逐步核對。可委派單一步驟給子代理，但等待其結束後才能開始下一步；平台不允許時使用內聯模式，不把使用本技能解釋為額外授權。

命令中的 SCRIPT 指 build/scripts/build_checkpoint.py，CONTEXT 指應用目錄下 niio-context.json。

1. 全新專案：確認沒有任何已發送的建立請求或遠端產物，建立空 context 後執行 `python3 SCRIPT init CONTEXT`。若沒有 context 但先前曾呼叫建立工具，視為結果不明，禁止初始化重建。
2. 每次恢復：執行 `python3 SCRIPT check CONTEXT`。退出碼 0 才可按 nextSteps 推進；2 表示步驟執行中／中斷待核對，1 表示格式、狀態或舊版檢查點問題。不可將錯誤當作新專案。
3. 開始步驟前：執行 `python3 SCRIPT begin CONTEXT --step STEP`，成功落盤後才呼叫遠端工具。重新讀取步驟檔案及其引用規則，遵守輸出契約。
4. 每次遠端成功立即保存真實 ID 與最小操作紀錄，再繼續同一步的下一個物件。只有排程器合併變更；不得刪除 buildState 或改寫 progress。
5. 完成整步：驗證實際交付物，然後 `python3 SCRIPT finish CONTEXT --step STEP --evidence "已核對的產物 ID、紀錄或驗證檔路徑"`。證據不可含憑證。腳本只記錄驗證聲明，不會驗證遠端，也不保證 API 冪等性。
6. 下一輪 check 後僅派發 nextSteps 中的一步。done 步驟不重跑；completed 且 nextSteps 空時僅回報結果。

### 中斷、逾時與舊專案

running 表示結果可能已生效，不能直接重試。先確認沒有其他執行器仍在工作，使用唯讀 MCP 依保存 ID、操作紀錄及規劃核對。確認整步全部完成，才能 finish；部分完成時只處理已核對確實缺少的物件，保留 running，不重新執行整步。查不到不等於不存在：清單不完整、名稱重複、權限不足、結果不確定時停止並請使用者確認。此流程不自動刪除、回滾或重送不明請求。

舊專案沒有 buildState 時 check 會停止，不能只用 progress 推定每一步完成。先唯讀核對整個已執行範圍，再由排程器備份 context 並建立 version=1 的 steps（所有步驟鍵皆必須存在；status 為 pending/running/done，done 附 evidence），保持 progress 與已驗證的連續完成階段一致。尚未確認的步驟記 running；failed、未知 progress 或順序衝突需人工處理，不得清空進度繞過。

.niio-build.lock 是單次檢查點寫入鎖，不是整個建置工作鎖。只允許一個排程器持有專案；存在鎖時停止，確認原程序已結束後才人工清理。恢復前檢查欄位、方案及交付物仍存在且與已記錄 ID 一致，缺檔時停止核對，不能只因 done 就忽略。

## 路由與驗證

順序：1 → 2 → 3 → 4 → 5 → 6 → 5b → 7 → 8 → 9 → 10 → 11 → 12。
逐步讀取 steps/ 中對應編號的檔案；10、11 另讀 workflow_rules.md；12 另讀 CAPABILITY_MATRIX.md。Step 3 仍使用保存的 MCP 回應整理欄位；Step 6 必須檢查 requiresReview。沒有規劃項目的步驟亦需記錄「已核對方案，無此項目」才能完成。
Step 9 寫回方案後必須驗證各工作流 nodes 非空；Step 10/11 必須核對實際發布結果。Step 12 依其說明記錄 CLI 已完成或待補項目，不能把待補說成已完成。CLI 的安裝、登入及帳號切換遵守平台授權規則，不因恢復流程自動變更帳號。

## 🔒 全域執行清單（標記 completed 前必須核對）

> [!CAUTION]
> 以下每一項都是**硬性交付物**。標記 `progress="completed"` 之前，必須逐項核對並確認全部完成。遺漏任何一項即為執行失敗。

| # | 交付物 | 驗證方法 | context 欄位 |
|---|--------|----------|-------------|
| 1 | 應用已建立 | `appId` 非空 | `appId` |
| 2 | 導航分組已建立 | `sectionIdByName` 條目數 = plan 中分組數 | `sectionIdByName` |
| 3 | 所有工作表已建立 | `worksheetIdByName` 條目數 = plan 中表數 | `worksheetIdByName` |
| 4 | 欄位結構已重新整理 | `worksheetContext.json` 非空且每表有 fields | `worksheetContext.json` |
| 5 | 自訂動作已建立 | `actionIdByName` 條目數 = plan 中動作數 | `actionIdByName` |
| 6 | 檢視已建立 | `viewIdByName` 條目數 = plan 中檢視總數 | `viewIdByName` |
| 7 | 示例資料已寫入 | 各表均有記錄 | `progress >= sample_data_created` |
| 8 | 頁面空殼已建立 | `customPageIdByName` 條目數匹配 plan | `customPageIdByName` |
| 9 | AI 助手已建立（若有） | `chatbotIdByName` 條目數匹配 plan（或 plan 無則跳過） | `chatbotIdByName` |
| 10 | 頁面元件已設定 | 所有頁面均已呼叫 `update_custom_page` | Step 7 完成 |
| 11 | 角色已建立 | `roleContext` 條目數 = plan 中角色數 | `roleContext` |
| 12 | 工作流已設計 | `niio-plan.json` 中每條 workflow 和 customActionWorkflow 的 `nodes[]` 非空 | `niio-plan.json` |
| 13 | 系統工作流已釋出 | 每個系統工作流 processId 已 publish | Step 10 完成 |
| 14 | 自訂動作工作流已釋出 | `customActionWorkflows[]` 每條均已 publish | Step 11 完成 |
| 15 | CLI 建後精修已對賬 | CLI 可用→已校正組織+設目前應用+回填 `cliGaps[]`；niio CLI 未安裝→已輸出待補清單且未中斷 | Step 12 完成 |

---


完成前逐項核對以上交付物。輸出應用連結、工作表與資料數量、已發布工作流、角色與助手數量、CLI 待補項目；任何未驗證內容須明確列出。不得偽造 ID、跳過步驟規則或宣稱離線測試證明遠端建置成功。
