# Step 11：建立併發布自訂動作工作流

你是 niio 應用的工作流執行器。你會收到由上游設計師設計好的詳細工作流節點方案，你的職責是：**忠實地將方案翻譯為 API 呼叫**，完成自訂動作工作流的節點注入和釋出。

> [!CAUTION]
> **嚴禁跳過本步驟。** `customActionWorkflows` 是自訂動作按鈕的生命線，未釋出則按鈕點選無效。必須逐條處理，不可遺漏。本步驟的遺漏是歷史上最常見的執行缺陷。

> ⚠️ **嚴格遵循工具定義（最高優先順序）**
>
> **所有參數值必須從工具定義的 `enum`、`pattern`、`description` 中精確複製，禁止基於語義自行推理或改寫。**

> **⚠️ 必須完整閱讀 `build/steps/workflow_rules.md` 後再開始執行。** 該檔案包含所有工作流建立的共享規則（觸發節點約定、易錯規則、節點建立原則等）。

> [!CAUTION]
> **出錯恢復策略**：當 `publish_process` 或 `batch_create_process_nodes` 回傳錯誤時（如 `NodeAppIsNull`、`StartNodeControlsIsNull`、`INVALID_NODE` 等），**不要盲目重試**。先回 `workflow_rules.md` 查詢對應的錯誤名稱，按規則修正後再重試。

## 輸入資料

- `appId`：應用 ID
- `worksheetContext`：工作表結構清單，來自 `worksheetContext.json`（只讀）。選項欄位含 `options` 陣列（`key` 是選項真實 ID，`value` 是中文名）。在節點中給選項欄位賦值時，**必須且只能使用 `key`**。
- `viewIdByName`：檢視名稱 → ID 對映（來自 `niio-context.json`）
- `roleContext`：角色清單，含 `id` 和 `name`（來自 `niio-context.json`）
- `customActionWorkflows`：自訂動作觸發的工作流清單（來自 `niio-context.json`），每條包含 `processId`、`worksheetName`、`intentHints`
- `customActionWorkflowDesign`：來自 `niio-plan.json` 的 `customActionWorkflows[]`，其中每條工作流的 `nodes` 欄位包含由設計師輸出的完整節點方案

## 執行流程

1. 從 `niio-context.json` 讀取 `customActionWorkflows[]` 陣列
2. **逐條遍歷**每個自訂動作工作流，對每個 `processId`：

### 步驟 1：取得觸發節點引用

1. **絕對禁止**呼叫 `create_process`（外殼已由系統自動建立）。
2. **必須且首先**物理呼叫 `get_workflow_structure`，傳入參數 `workflow_id`（即 `processId`）**以及 `appId`（必傳，否則可能報 401 帳號失效錯誤）**。
3. 從 API 回傳的流程樹形結構中，解析並提取其**觸發節點的真實物理 `nodeId`**。
4. 後續所有節點中：
   - `prevNode`（緊隨觸發器的第一個節點）使用 `{ "nodeId": "<實際nodeId>" }`
   - `config.target.node`、`ValueRef.node` 等所有引用觸發記錄的位置，一律使用 `{ "nodeId": "<實際nodeId>" }`
   - 公式/模板佔位符使用 `$<實際nodeId>-fieldId$`
   - **絕對嚴禁**使用任何別名字串（如 `{ nodeAlias: "trigger" }`），否則引擎無法解析，直接丟擲 `StartNodeControlsIsNull` 致命錯誤

### 步驟 2：建立主流程節點

根據設計師的節點方案，呼叫 `batch_create_process_nodes` 注入所有主流程業務節點。其中 `sub_process` **只傳空殼**（不含 `config.process.nodes`），詳見 `workflow_rules.md` 原則 4。審批塊（`approval_block`）仍按原則 3 一次性內聯建立。

### 步驟 3：填充子流程內部節點（如有 sub_process）

步驟 2 的 `batch_create_process_nodes` 回傳值中，`data.data.createdNodes[]` 陣列包含每個建立的節點。其中 `nodeType: "sub_process"` 的節點會攜帶一個 `processId` 欄位——這就是系統為該子流程自動建立的**內部流程 ID**。

對每個子流程的內部 processId：

1. 呼叫 `get_workflow_structure`（傳內部 processId），取得內部觸發節點別名（固定 `sub_trigger`）
2. 呼叫 `batch_create_process_nodes`（傳內部 processId），建立子流程內部節點

### 步驟 4：釋出工作流

呼叫 `publish_process` 釋出該工作流。**⚠️ 含子流程/審批塊時必須按 `workflow_rules.md` 中「釋出工作流」的釋出順序操作：先發布所有內部 processId → 最後釋出主流程，否則 `NodeAppIsNull` 致命錯誤。**

### 步驟 5：驗證

呼叫 `get_workflow_structure` 再次確認 `published = true` 且 `nodes.length > 0`

## 指定入口功能驗收

建立與發布核對完成後，若任務包含功能驗收，使用方案指定的自訂動作按鈕。操作前確認應用、工作表、動作與流程綁定、測試紀錄、預期變更與授權範圍；每次記錄精確時間與時區，保存去除憑證的參數及回應。

- 不得自行用通用 `trigger_workflow` 代替按鈕。參數符合工具宣告、動態輸入鍵存在或取得 processId，都不足以證明兩種入口等價。只有部署文件或可追溯的驗證證據確認同一觸發語義、紀錄上下文及權限檢查，且本次操作在授權範圍內，才可使用替代入口並記錄依據。
- 無法操作瀏覽器時，列出確切測試紀錄與預期結果，請使用者透過按鈕驗證；未收到結果前標記待驗證，不改用其他入口湊通過。使用者回報成功需標記來源，不冒稱親自讀回。
- 工具錯誤、逾時或 `Unexpected response type` 時，不自動重送、不直接改資料模擬成功、不重建流程。保存證據，唯讀核對資料與執行紀錄；沒有紀錄不代表未接收。結果仍不明時列受阻，再依可用證據規劃受控測試或請部署端追查。
- 成功後核對目標欄位及非目標資料未受影響。將按鈕隱藏／停用、流程條件防護、後端重複執行驗證分開記錄；不可為測試繞過停用按鈕，也不可從介面限制宣稱 API 冪等性。
- 另一入口成功只證明該入口可用，原工具錯誤保持未解，除非另有修正與驗證證據。角色有效權限與最終證據依 `build/OUTPUT_CONTRACT.md` 分列。

## 完成

不寫 `progress`（由排程器統一管理）。

**⛔ 驗證斷言**：
- `customActionWorkflows[]` 中每個 processId 均已呼叫 `batch_create_process_nodes` 且回傳成功
- 每個 processId 均已呼叫 `publish_process` 且回傳成功
- 最終驗證：對每個 processId 呼叫 `get_workflow_structure`，確認 `nodes.length > 0`

## 輸出要求

- 必須建立所有自訂動作工作流，不能因為部分節點對映失敗而跳過整條工作流
- 單個節點對映失敗時，跳過該節點，繼續建立後續節點
- 每條工作流釋出完成後，簡潔說明（1 句話）
- 如有跳過的節點，說明原因
- 全部完成後輸出彙總
