# 自訂動作按鈕（記錄按鈕）

## 呼叫正規化

```bash
# 列出工作表上的按鈕
hap worksheet custom-actions <worksheetId>
hap worksheet custom-actions <worksheetId> --view-id <viewId>   # 只看該檢視顯示的
hap worksheet custom-actions <worksheetId> --kind ai            # 只看 AI 動作（另一檔是 action）
hap worksheet custom-actions <worksheetId> --deleted            # 已刪除的按鈕
hap worksheet custom-actions <worksheetId> --record-id <rowid>  # 這條記錄上哪些按鈕能點

# 模式一：--action-spec 高層宣告（推薦）
hap worksheet create-custom-action <worksheetId> -a <appId> --action-spec '{
  "name": "標記完成",
  "type": "updateCurrentRecord",
  "updateFields": ["<controlId>"],
  "confirm": true,
  "confirmMsg": "確認標記為完成嗎？",
  "enableWhen": {"logic":"and","items":[
    {"field":"<狀態列>","op":"ne","value":"<已完成選項key>"}]}
}'

# 模式二：--config 原始 wire 設定，原樣下發
hap worksheet create-custom-action <worksheetId> -a <appId> --config '{...}'

# 原地更新：帶 --btn-id，在原按鈕上改
hap worksheet create-custom-action <worksheetId> -a <appId> \
  --btn-id <btnId> --action-spec '{...}'

# 刪除（永久，不進回收站）
hap worksheet delete-custom-action <worksheetId> <btnId> -a <appId> -y

# 「從某個檢視裡撤下」是另一回事，不是刪除
hap worksheet delete-custom-action <worksheetId> <btnId> --view-id <viewId>
hap worksheet delete-custom-action <worksheetId> <btnId> --view-id <viewId> --placement list
```

坑位提示：

- **兩種模式二選一**：`--action-spec` 是乾淨的高層結構，由命令降級為 wire 設定；`--config` 是原始 wire 形態，原樣傳送。不要混填。
- 每個按鈕建立時會**自動生成一條關聯的自動化流程**，命令會把它的 processId 一併回傳，方便接著搭流程。**後續修改必須帶 `--btn-id` 原地更新**——不帶就會新建一個按鈕和一條新流程，老流程上的設定全丟。
- **`updateFields` 裡每個欄位的填寫模式，跟著欄位自己在工作表上的設定走**：工作表上必填的欄位
  在按鈕表單上也必填，其餘是選填，本來就不能填寫的型別（附件、公式、備註…）只讀展示。不需要、
  也不應該自己去指定檔位。
- **`enableWhen` 一給，按鈕就自動變成「滿足條件才可用」**，不用再手工設別的開關。篩選門檻二選一：
  `enableWhen` 用統一篩選寫法（推薦，如 `{"logic":"and","items":[{"field":"<狀態列>","op":"ne","value":"<已完成選項key>"}]}`），
  或 `filters` 直接給 wire 形態陣列。寫法與按鈕上可用的比較方式見 `hap guide record filter`（3.2 那張表的
  「檢視/規則/按鈕/圖表」一列）。
- **`confirm` 一給，按鈕就真的彈二次確認框**；`confirmMsg` 是框裡的文案，不給用預設文案（按當前
  CLI 語言寫入按鈕）。任何 type 都能疊加。
- **`--view-id` 撤下按鈕只對「限定了顯示檢視」的按鈕有效**。按鈕設成「所有檢視都顯示」時沒有
  「某個檢視的成員資格」可撤，命令會直接報錯讓你先限定顯示檢視，而不是假裝撤下了。
  `--placement` 配合 `--view-id`：`list` 只從記錄行撤，`detail` 只從記錄頁撤，不給就兩處都撤。

## 資料字典

字典核對於 niio CLI 0.9.0；未覆蓋的鍵以讀命令回傳的實際結構為準。

### action_spec 鍵表（--action-spec 輸入）

未列出的鍵會被忽略。worksheetId / appId / btnId 由命令列參數提供，不要寫進 JSON。

| 鍵 | 含義 | 值形態 |
|---|---|---|
| name | 按鈕顯示名 | string |
| desc | 按鈕描述 | string（預設 ""） |
| type | 動作型別，預設 triggerWorkflow | enum `updateCurrentRecord` \| `createRelatedRecord` \| `triggerWorkflow` |
| updateFields | （updateCurrentRecord）彈窗中要填寫的欄位；每項的填寫模式由該欄位自身的必填/可寫性推導 | `["<controlId>", ...]` |
| relationField | （createRelatedRecord）新記錄寫入的關聯欄位 | controlId string |
| relationControl | （createRelatedRecord）配套透傳值 | string（預設 ""） |
| enableWhen | 按鈕可用條件（滿足篩選才顯示） | 統一寫法 `{logic, items:[{field, op, value}]}`；舊的 wire 陣列 → [FilterCondition[]](../scripts/types/filter-condition.schema.json) 也收 |
| filters | enableWhen 的 wire 形態替代寫法 | wire 篩選陣列（與 enableWhen 二選一） |
| confirm | 強制二次確認彈窗 | bool |
| confirmMsg | 確認彈窗文案 | string（預設 "你確認執行此操作嗎？"） |
| sureName | 確認按鈕文案 | string（預設 "確認"） |
| cancelName | 取消按鈕文案 | string（預設 "取消"） |
| isAllView | 在所有檢視顯示 | int 0/1（預設 1） |
| verifyPwd | 執行前要求驗證密碼 | bool（預設 false） |
| workflowId | 指定按鈕驅動的流程（預設 "" = 用自動生成的那條） | string |
| runWorkflowAfterSubmit | 顯式決定提交後跑不跑流程，**覆蓋下表的 workflowType** | bool（true→1、false→2；不給就按 type 定） |
| icon / color / showType / isBatch | wire 鍵直通，原樣複製 | 按 wire 鍵表 |
| advancedSetting | **不是原樣複製**，見下方「advancedSetting 會被改寫」 | 字串值的物件 |
| listViews / detailViews | 按鈕在哪些檢視上出現（行內 / 記錄頁） | viewId 陣列，落庫時序列化成字串並改名 `listviews` / `detailviews` |

`desc` 還有個未寫在別處的別名：不給 `desc` 時會取 `remark`（V3 用後者命名懸浮說明）。

### type → wire 降級對映

| spec type | clickType | writeType | writeObject | 額外 wire 鍵 |
|---|---|---|---|---|
| updateCurrentRecord | 3（填寫） | 1（填寫欄位） | 1（本記錄） | `writeControls: [{controlId, type}]`，type 按欄位推導（見下）；`workflowType: 2` |
| createRelatedRecord | 3（填寫） | 2（新建關聯記錄） | 2（關聯記錄） | `addRelationControlId`、`relationControl`；`workflowType: 2` |
| triggerWorkflow（預設） | 1（立即執行）；帶 confirm 時 2（二次確認） | ""  | "" | `workflowType: 1` |

**`workflowType` 不是固定 1**：1=提交後執行那條流程、2=不執行。填寫類的兩種按鈕下發 2，
`triggerWorkflow` 下發 1；給了 `runWorkflowAfterSubmit` 則以它為準。固定下發的只有 `isAllView`。

**填寫類按鈕的二次確認靠 `enableConfirm`，不是 `clickType`**：`clickType` 為 3 時給了
`confirm` / `confirmMsg`，介面卡會另外下發 `enableConfirm: true`——少了它，確認文案存進去了但對話方塊不出現。

### advancedSetting 會被改寫

走 `--action-spec` 時 `advancedSetting` **不是原樣複製**：

- 三個鍵每次都補齊（你沒給才補）：`remarkrequired="1"`（備註必填）、`remarkname`（備註框標題）、
  `tiptext`（完成提示），少了它們確認框裡是個沒標題的理由框。
- `listViews` / `detailViews` 會被序列化成 JSON 字串，並改名成小寫的 `listviews` / `detailviews` 落庫。

**`writeControls[].type` 由欄位自身推導，不是固定值**：不可寫的型別（附件、公式、備註…）給 `1`
只讀，工作表上必填的欄位給 `3` 必填，其餘給 `2` 填寫。走 `--action-spec` / edit-spec 的
`action_spec` 都會這樣推；**只有裸 `config` 不會**（見下）。

### wire config 鍵表（--config 輸入 / custom-actions 回傳）

| 鍵 | 含義 | 值形態 |
|---|---|---|
| name | 按鈕名 | string |
| desc | 描述 | string |
| clickType | 點選行為 | int enum：1=立即執行，2=二次確認，3=填寫 |
| writeType | 填寫型別 | int enum：1=填寫欄位，2=新建關聯記錄 |
| writeObject | 填寫物件 | int enum：1=本記錄，2=關聯記錄 |
| writeControls | 填寫欄位清單 | `[{controlId, type}]`；type：1=只讀，2=填寫，3=必填 |
| addRelationControlId | 新建關聯記錄的目標關聯欄位（**寫入用這個鍵；`custom-actions` 讀回來叫 `addRelationControl`，無 `Id` 字尾**） | controlId string |
| relationControl | 關聯配套值 | string |
| showType | 顯示條件 | int enum：1=一直顯示，2=滿足篩選條件；**沒設門控的按鈕讀回來可能是 `0`**，以讀回值為準 |
| filters | 顯示/可用篩選 | → [FilterCondition[]](../scripts/types/filter-condition.schema.json) |
| isAllView | 所有檢視顯示 | int 0/1 |
| workflowType | 流程驅動標記 | int（固定 1） |
| confirmMsg / sureName / cancelName | 二次確認文案三件套 | string |
| icon / color | 圖示與顏色 | string |
| isBatch | 允許批次執行 | bool |
| enableConfirm | 填寫類按鈕（clickType 3）的二次確認開關 | bool；走 action_spec 時由 confirm 推導，裸 config 要自己給 |
| verifyPwd | 執行前驗證密碼 | bool |
| workflowId | 按鈕驅動的流程 id | string |
| btnType / displayViews / status / iconUrl / updateTime / updateAccountId | 讀回還會帶這些，改按鈕時原樣保留即可 | 以讀命令回傳為準 |
| advancedSetting | 高階設定 | object（以讀命令回傳為準） |

## 🚨 edit-spec 裡的 `config` 是原始逃生口，不經適配

`custom-action.create` / `custom-action.update` 兩個 op 都能二選一地給 `action_spec` 或 `config`。
給 `config` 時它按原樣發出，**介面卡做的事一件都不發生**：

- `clickType` / `writeType` / `writeObject` 的配對不會補
- `showType` 不會因為你寫了篩選而切到「滿足條件才顯示」
- 填寫類按鈕的二次確認（`enableConfirm`）不會設
- `writeControls[].type` 不會按欄位推導，全部落到預設檔

它是「介面卡造不出來的形狀」的正當出口，但走它就等於放棄上面所有保護。**能用 `action_spec`
就別用 `config`**；確實要用，就自己把整份 wire 設定寫全。
