# 工作流共享規則

> 本檔案被 `10_create_workflows.md` 和 `11_create_action_workflows.md` 共同引用。閱讀步驟檔案時**必須完整閱讀本檔案**。

---

## 觸發節點引用約定

本文件中使用 **`<triggerNodeRef>`** 作為觸發節點引用的通用佔位符。實際傳值時，必須根據工作流型別替換為正確的值：

| 工作流型別 | 如何取得觸發節點引用 | `node` 傳值格式 | 公式/模板佔位符格式 |
| :--- | :--- | :--- | :--- |
| **普通工作流**（`create_process` 新建） | **優先**從 `create_process` 回傳的 `triggerAlias` 欄位（與 `processId` 同級）直接取觸發節點別名；僅當該欄位缺失時才回退調 `get_workflow_structure` 取 `trigger.nodeAlias`——**不要在已拿到 `triggerAlias` 後再多讀一次**（重複往返） | `{ "nodeAlias": "<实际别名>" }` | `$<实际别名>-fieldId$` |
| **自訂動作工作流**（方案自帶 `processId`） | 呼叫 `get_workflow_structure` 後，從回傳結果中提取觸發節點的物理 `nodeId` | `{ "nodeId": "<实际nodeId>" }` | `$<实际nodeId>-fieldId$` |

> ⚠️ **絕對禁止假設觸發節點的別名是固定字串（如 `"trigger"`）。** 觸發節點的別名由系統分配，不同工作流各不相同。自訂動作工作流的觸發節點甚至沒有可用的別名，只能使用物理 `nodeId`。如果使用了錯誤的別名，釋出校驗將丟擲 `StartNodeControlsIsNull` 致命錯誤。

## 名稱 → ID 對映規則

方案中使用中文名稱引用工作表和欄位，你必須從 `worksheetContext` 中查詢對應的真實 ID：

- **工作表名稱** → `worksheetContext[].name` → 取 `id`
- **欄位名稱** → `worksheetContext[].fields[].name` → 取 `id`
- **選項值名稱** → `worksheetContext[].fields[].options[].value` → 取 `key`
- **角色名稱** → `roleContext[].name` → 取 `id`
- **檢視名稱** → `viewIdByName["工作表名/视图名"]` → 取 viewId

> 🚫 **fieldId 必須使用欄位的真實 `id`，嚴禁使用欄位的 `alias`。** 工作流 API 不識別 alias。

> ⚠️ **禁止自行編造 ID**。如果方案中提到的名稱在 `worksheetContext` 中找不到，跳過該節點並說明。

> ⚠️ **所有 ID 必須原樣複製**。從 worksheetContext / roleContext / viewContext 中取到的 ID（包括 24 位 hex fieldId 和 GUID 格式的 roleId），必須**逐字元原樣複製**到工具參數中，嚴禁手動重新輸入或憑記憶拼寫——GUID 類 ID 長達 36 字元，手寫極易多字元或少字元導致引用無效。

### 降級策略

- **角色找不到**：從 `roleContext` 中選擇語義最接近的角色替代；若為空，改用 `{ kind: "triggerUser" }`
- **roleId 導致 API 報錯**（如 `batch_create_process_nodes` 回傳角色相關錯誤）：從 recipients 中去掉該角色引用後重試；若該角色是唯一接收者（去掉後 recipients 為空），改用 `{ kind: "triggerUser" }` 兜底，確保工作流可釋出
- **檢視找不到**：使用該工作表的第一個檢視

## 易錯規則

### fieldId 必須用真實 ID，絕對嚴禁使用 alias

niio 工作流物理引擎在解析節點邏輯時**完全不識別欄位的 alias**（如 `status`、`title` 等）。如果在工作流設定中傳入 alias，會導致邏輯靜默丟失或產生 `INVALID_FIELD` 報錯。所有引用欄位 ID 的位置，必須從 `worksheetContext` 中對映出真實的 24 位十六進位制欄位 ID！

此規則適用於所有包含 `fieldId` 的物理設定：
- `ValueRef.fieldId`、`FieldValueRef.fieldId`
- `FieldPatch.fieldId`
- `Condition.left.fieldId`、`Condition.right.fieldId`
- `config.formula` 中 `$nodeAlias-fieldId$` 的 fieldId 部分（含觸發節點引用，詳見「觸發節點引用約定」）
- `config.content` / `config.body` 模板中的 fieldId 部分
- `trigger.config.trigger_fields[]`

---

### Condition：left.node 始終必填

Condition 結構為 `{ left, op, right }`。其中 `left` 屬於 `FieldValueRef`，**`node` 屬性絕對不能預設**（即使是查詢節點自身的內部過濾條件）。

- **查詢節點自身的 filter（如 `get_single` / `get_multiple`）**：`left.node` **必須且只能引用當前查詢節點自身**；`right` 引用上游節點（如觸發節點或更早的查詢節點）以提供動態過濾值。
  
  *示例*（查詢節點 `find_book` 的 filter 中，`left.node` 指向 `find_book` 自身，`right.node` 指向上游節點）：
  ```json
  {
    "logic": "and",
    "items": [
      {
        "left": { "kind": "field", "node": { "nodeAlias": "find_book" }, "fieldId": "674046935a63abb6377d23a1" },
        "op": "eq",
        "right": { "kind": "field", "node": "<triggerNodeRef>", "fieldId": "674046935a63abb6377d23ff" }
      }
    ]
  }
  ```

- **分支節點 filter（`branch`）**：`left.node` 必須引用分支上游的某個資料源節點。
- **觸發器 filter**：`left.node` 引用觸發節點自身（按「觸發節點引用約定」傳值）。

---

### Condition.op 合法列舉

> ⚠️ niio 工作流僅支援以下運算子字面值，**禁止使用任何其他運算子**（如 `ge`/`le`/`is_empty`/`neq` 等變體）：

`eq`（等於）· `ne`（不等於）· `gt`（大於）· `gte`（大於等於）· `lt`（小於）· `lte`（小於等於）· `in`（屬於陣列）· `not_in`（不屬於陣列）· `empty`（為空）· `not_empty`（不為空）· `contains`（包含）· `not_contains`（不包含）· `starts_with`（開頭是）· `ends_with`（結尾是）· `all_contains`（同時包含）· `belongs`（屬於部門/組織）· `not_belongs`（不屬於部門/組織）· `checked`（已勾選）· `unchecked`（未勾選）

---

### 查詢結果分支處理規範

- **`get_single` 結果分支判空**：直接在下游 `branch` 中判斷該查詢節點的 `rowid` 是否為 `not_empty`：
  
  ```json
  {
    "left": { "kind": "field", "node": { "nodeAlias": "find_single_book" }, "fieldId": "rowid" },
    "op": "not_empty"
  }
  ```

- **`get_multiple` 結果分支判空**：**絕對嚴禁**直接判斷 `get_multiple` 節點的 `rowid`。必須採用以下二階段鏈式邏輯：
  1. **步驟一**：先緊隨其後建立一個 `rollup`（彙總統計）節點，對 `get_multiple` 節點的記錄進行 `COUNT` 聚合。
  2. **步驟二**：在 downstream 的 `branch` 條件分支中，判斷該 `rollup` 節點輸出的 `number_fx_id` 欄位是否大於 0。
  
  *完整串聯示例*：
  ```json
  // 1. 创建 rollup(count) 节点
  {
    "nodeAlias": "count_overdue",
    "nodeType": "rollup",
    "config": {
      "method": "count",
      "target": { "kind": "record", "node": { "nodeAlias": "find_overdue_records" } }
    }
  }
  // 2. 分支判断 rollup 输出（固定字段 number_fx_id）
  {
    "left": { "kind": "field", "node": { "nodeAlias": "count_overdue" }, "fieldId": "number_fx_id" },
    "op": "gt",
    "right": { "kind": "literal", "value": 0 }
  }
  ```

---

### config.target 而非 sourceNode

niio `NodeSpec` 基礎模式上**完全沒有 `sourceNode` 屬性**。凡是需要指定資料源記錄的節點，必須將設定寫在 `config.target` 內，使用 `RecordValueRef`（`kind` 固定為 `"record"`）：

- **✅ 正確示例**：
  ```json
  {
    "nodeAlias": "update_status",
    "nodeType": "update_record",
    "config": {
      "target": { "kind": "record", "node": "<triggerNodeRef>" },
      "fields": [...]
    }
  }
  ```
- **❌ 錯誤示例**：`{ "sourceNode": { ... }, "config": { ... } }` （API 會靜默報錯丟棄）

---

### 分支路徑（branch path）的使用與引用約束

分支路徑的 alias 僅作為組織節點層級結構的路由標記：
- ❌ **絕對不能作為下游任何節點的 `prevNode`**：分支路徑內的第一個子節點，其 `prevNode` 物理指向該路徑的 alias，其 `parentNode` 也必須指向該路徑的 alias。路徑內部後續節點的 `prevNode` 指向路徑內部的前一個節點。
- ❌ **絕對不能作為 `target.node` 的值**：如 `cc`、`update_record` 節點的 `config.target.node` 必須指向具體的觸發器節點或 `get_single` 節點，**絕不能指向分支路徑 alias**。

---

### send_email / send_internal_notice / cc 正文模板高標準

- **嚴禁使用 literal 盲盒正文**：正文絕對不要只寫一行"您有新的審批，請處理"這種寬泛籠統、對收件人無實質價值的文字。
- **高標準格式**：`config.content`（send_internal_notice / cc）和 `config.body`（send_email）必須物理傳 `{ "kind": "template" }`，並透過 `$nodeAlias-fieldId$` 嵌入關鍵業務欄位（如申請人、單號、日期、費用等）。send_email 推薦將 `bodyType` 設定為 `"html"` 做精美拼接。其中 `nodeAlias` 部分引用觸發節點時，需按「觸發節點引用約定」使用實際別名或 nodeId。
  
  *HTML 郵件高模擬示例*（假設觸發節點別名為 `start`）：
  ```json
  {
    "subject": { "kind": "template", "value": "借阅超时告警：$start-674046935a63abb6377d23a1$ 已经超期" },
    "body": {
      "kind": "template",
      "value": "<h3>图书超期未归还温馨提醒</h3><p><b>借阅人：</b>$start-674046935a63abb6377d23b2$</p><p><b>图书名称：</b>$start-674046935a63abb6377d23a1$</p><p><b>应还日期：</b>$start-674046935a63abb6377d23c5$</p><p>请尽快将图书归还至服务台，谢谢您的配合！</p>"
    },
    "bodyType": "html"
  }
  ```

---

### approve / fill_in 審批填寫塊設計規範

- **`allowReject` 物理使能**：對於審批（`approve`）節點，預設的 `allowReject` 是 `false`。在絕大多數真實業務中，必須顯式將其設定為 `true`，以允許審批人拒絕申請。
- **`fill_in` 節點的 `assignee` 限制**：填寫節點的 `assignee` 是**單個 `PersonRef` 結構**（非陣列），且 `formProperties`（要填寫的表單屬性）必須至少宣告一項。

---

### rollup / compute 物理輸出欄位常數

當下遊節點（如通知正文或更新節點）想要引用 `rollup`、`compute` 或 `code` 節點的輸出結果時，必須使用以下系統固定的常數欄位 ID 或自訂參數名：

| 節點型別 | 參數設定型別 | 必填 config 欄位 | 物理輸出欄位 ID | 下游引用佔位符示例 |
| :--- | :--- | :--- | :--- | :--- |
| **`rollup`** | `method: "count"`（統計上游多條記錄） | `target`（引用 get_multiple 節點），**不傳** worksheetId/fieldId | **`number_fx_id`** | `$nodeAlias-number_fx_id$` |
| **`rollup`** | `method: "count"`（直接統計工作表記錄，支援 `filter`） | `worksheetId`，**不傳** fieldId 或 target | **`number_fx_id`** | `$nodeAlias-number_fx_id$` |
| **`rollup`** | `method: "sum/avg/average/min/max/filled/not_filled"`（支援 `filter`） | `worksheetId` + `fieldId`，**不傳** target | **`number_fx_id`** | `$nodeAlias-number_fx_id$` |
| **`compute`** | `computeType = "number"` | `expression` | **`number_fx_id`** | `$nodeAlias-number_fx_id$` |
| **`compute`** | `computeType = "dateDiff"` | `startTime` + `endTime` + `outputUnit` | **`number_fx_id`** | `$nodeAlias-number_fx_id$` |
| **`compute`** | `computeType = "dateOffset"` | `inputTime` + `offsetExpression` | **`date_fx_id`** | `$nodeAlias-date_fx_id$` |
| **`code`** | 程式碼塊 | `code` + `inputs` + `outputs` | **自訂輸出名 `name`** | `$nodeAlias-outputName$` |

#### ⚠️ dateOffset 型別的日期偏移計算語法極其嚴格：
- 偏移量表示式 `offsetExpression` 必須包含正負號和單位（例如 `"+30d"`、`"+3d"`、`"-1d"`），大小寫敏感。如果只寫數字或不帶單位，在釋出校驗階段會直接報 `INVALID_NODE offsetExpression 格式不正确` 致命錯誤。
- 它的物理輸出欄位 ID 固定為 `date_fx_id`，下游節點引用其結果時必須使用 `$nodeAlias-date_fx_id$` 的形式。

---

### 避免 `StartNodeControlsIsNull` 釋出校驗錯誤

- **`update_record`（更新記錄）節點執行後並沒有暴露輸出控制欄位（輸出 controls 為空）。**
- **絕對不能**在後續節點（如站內通知、審批、更新等）中透過形如 `$update_record_node-fieldId$` 強行引用更新記錄節點的欄位值。如果強行引用，niio流程釋出校驗將直接攔截丟擲 `StartNodeControlsIsNull`（起始節點設定控制為空或不存在）的致命阻斷錯誤。
- **標準避錯做法**：後續節點需要使用該記錄的欄位值時，應該直接追溯並引用觸發源記錄（如 `$<triggerNodeAlias>-fieldId$`）或之前透過查詢節點取得到的物理記錄（如 `$get_single_node-fieldId$`）。

---

## description 必填

- **流程 description**：呼叫 `create_process` 時，`description` 欄位**必須填寫**，用一句話概括該工作流的整體業務目的（如"當合同狀態變更為已簽署時自動通知相關人員並更新回款計劃"）。
- **節點 description**：每個節點的 `description` 欄位**必須填寫**，用一句話描述該節點的業務意圖（如"查詢當前使用者名稱下所有未完成的訂單"、"將狀態更新為已審批並記錄審批時間"）。description 不是 name 的復讀，而是對**為什麼需要這個節點、它在流程中的作用**的補充說明。

---

## 節點建立原則

### 原則 1：同層節點儘量一次建立

同一層級的非分支節點，應合併到一次 `batch_create_process_nodes` 呼叫中。

### 原則 2：分支處理

分支節點的 `config.paths` 定義路徑別名和條件。路徑下的子節點透過 `parentNode` 掛入對應路徑。

> ⚠️ 分支後不允許用 `prevNode` 直接接分支節點。分支後的所有節點必須透過 `parentNode` 掛到某個路徑下。

> ⚠️ 分支路徑下的第一個節點，`prevNode` 必須顯式指向該路徑的 alias（與 `parentNode` 相同）。

### 原則 3：審批塊——兩步建立

審批塊使用 `nodeType: "approval_block"`，**分兩步建立**：

**第一步：建立空審批塊**（`config.process` 只傳 `mode` 和 `name`，**不傳 `nodes`**）

```json
{
  "nodeAlias": "approval",
  "nodeType": "approval_block",
  "prevNode": "<triggerNodeRef>",
  "config": {
    "target": { "kind": "record", "node": "<triggerNodeRef>" },
    "initiators": [{ "kind": "field", "node": "<triggerNodeRef>", "fieldId": "ownerid" }],
    "process": {
      "mode": "create",
      "name": "审批流程"
    }
  }
}
```

**第二步：建立內部節點**——從第一步 `batch_create_process_nodes` 回傳值的 `createdNodes` 中，找到該審批塊節點，提取其內部 `processId`，再調一次 `batch_create_process_nodes`（傳內部 `processId`）建立審批內部節點。

> ⚠️ **`initiators` 是必填項**：審批塊必須顯式指定發起人。常見做法是繫結觸發記錄的擁有者：`{ "kind": "field", "node": <triggerNodeRef>, "fieldId": "ownerid" }`。不傳此欄位會導致 `config.initiators: 不能为空` 致命校驗錯誤。

> ⚠️ 審批內部節點引用記錄時，使用 `{ nodeAlias: "approval_start" }`（固定別名）。**絕對不能**使用外部主流程的觸發節點別名（如 `trigger`、`start` 等），因為審批子流程無法跨作用域識別外部別名，會導致 `找不到节点别名` 致命報錯。

> 🚫 **審批塊物理名稱空間隔離（極易踩坑）**：
> `approval_block` 內部與外部主流程是**完全隔離的執行上下文**：
> - 內部節點的 `prevNode` **不能**指向外部主流程中的任何節點
> - 外部主流程的節點 `prevNode` **不能**指向內部節點
> - 內部節點引用被審批的記錄時，**只能**使用固定別名 `{ nodeAlias: "approval_start" }`，不能使用外部觸發節點的別名
>
> 違反上述任一規則，均會觸發 `prevNode 找不到` 或 `找不到节点别名` 的致命校驗錯誤。

> ⚠️ **審批結果分兩層**（必須明確區分放置位置）：
> - **審批內部**（第二步建立的內部節點中）：在 `approve` 節點之後新增 `branchType: "approval_result"` 分支，用於寫入審批人（`executorid`）、審批意見（`opinionSummary`）等審批詳細資訊到記錄中
> - **主流程**（放在 `approval_block` 節點之後的外部主流程中）：用 `branch` 判斷審批塊的最終 `result`（`PASS` / `OVERRULE`），用於根據透過/駁回結果更新主記錄的業務狀態、傳送通知等

### 原則 4：子流程——兩步建立

子流程使用 `nodeType: "sub_process"`，**分兩步建立**（與審批塊相同）：

**第一步：建立空子流程**（`config.process` 只傳 `mode`、`name` 和可選的 `start.inputFields`，**不傳 `nodes`**）

如果設計方案中子流程的內部節點透過「外層」字首引用了外部主流程的資料（如："外層觸發記錄.客戶名稱"），你必須自己歸納這些外部引用，在第一步的 `config.process.start.inputFields` 中自動為其宣告對應的輸入參數：

```json
{
  "config": {
    "process": {
      "mode": 1,
      "name": "逐条处理XX",
      "start": {
        "inputFields": [
          {
            "fieldId": "child_message",
            "name": "通知内容",
            "type": "text",
            "required": true,
            "description": "从父流程传入的通知文本"
          }
        ]
      }
    },
    "input": [
      {
        "fieldId": "child_message",
        "op": "set",
        "value": { "kind": "field", "node": { "nodeAlias": "start" }, "fieldId": "674...a1" }
      }
    ]
  }
}
```

- `inputFields[].fieldId`：參數穩定 ID，父流程賦值 + 子流程內部引用用
- `inputFields[].type`：`text`/`number`/`datetime`/`user`/`department`/`orgRole`/`array`/`objectArray`
- `config.input[].fieldId`：必須與 `inputFields[].fieldId` 一一對應
- `config.input[].value`：標準 ValueRef（`literal`/`field`/`systemField`/`template`）

**第二步：建立內部節點**——從第一步 `batch_create_process_nodes` 回傳值的 `createdNodes` 中，找到該子流程節點，提取其內部 `processId`，再調一次 `batch_create_process_nodes`（傳內部 `processId`）建立子流程內部節點。

> ⚠️ **子流程內部資料作用域**：
> - 子流程開始節點固定別名 `sub_trigger`，代表當前正在處理的那條記錄
> - 子流程內部節點引用當前記錄時，使用 `{ nodeAlias: "sub_trigger" }`
> - 子流程參數在內部用 `$process_variable-fieldId$`（template kind）引用，**不要用 `$sub_trigger-fieldId$` 引用參數**；`sub_trigger` 只代表記錄資料源
> - 不使用 `inputFields` 時，**子流程無法跨作用域引用主流程節點**
> - 子流程內部可以有自己的查詢節點，後續節點可引用內部查詢節點的 alias

> 分支、審批塊和子流程可以任意巢狀。

---

## 全域約束

- 節點中引用的 `worksheetId`、`fieldId` 必須來自 `worksheetContext`，**必須使用 ID，不能使用別名，不能自行編造**

## nodeAlias 命名

- 使用英文蛇形命名法，簡短且語義明確
- 示例：`find_related_book`、`update_stock`、`notify_applicant`
- 禁止使用中文、無意義序號

## 節點定位

- `prevNode`：前驅節點（執行順序）。分支路徑下的第一個節點填該路徑 alias
- `parentNode`：容器歸屬。分支路徑下的子節點填對應的路徑 alias

## 資料引用規範

### ValueRef 的 6 種 kind

節點設定中所有值引用（`ValueRef`）透過 `kind` 欄位決定取值方式。**選錯 kind 是最常見的構造錯誤。**

| kind | 用途 | 必填屬性 | 示例 |
|---|---|---|---|
| `field` | 引用上游節點的欄位值 | `node` + `fieldId` | `{ kind: "field", node: { nodeAlias: "find_book" }, fieldId: "674...a1" }` |
| `systemField` | 引用系統級參數 | `fieldId` | `{ kind: "systemField", fieldId: "nowTime" }` |
| `literal` | 固定值 | `value` | `{ kind: "literal", value: "已完成" }` |
| `record` | 引用整條記錄（用於 target 和關聯記錄欄位賦值） | `node` | `{ kind: "record", node: { nodeAlias: "sub_trigger" } }` |
| `template` | 模板字串（含佔位符） | `value` | `{ kind: "template", value: "$start-674...a1$" }` |
| `empty` | 顯式空值 | 無 | `{ kind: "empty" }` |

> ⚠️ **`systemField` 不需要也不能攜帶 `node` 屬性。** 它是全域系統值，與任何節點無關。在模板中引用系統欄位時，必須使用固定字首 `system`，格式為 `$system-fieldId$`（如 `$system-nowTime$`）。**嚴禁**使用任意節點別名（如 `$sub_trigger-nowTime$`）——這會被引擎解析為該節點上名為 `nowTime` 的業務欄位（不存在），導致靜默丟失。

### systemField 合法列舉

| fieldId | 含義 | 常見用途 |
|---|---|---|
| `nowTime` | 節點執行時的當前時間 | compute 日期差/偏移的 startTime/endTime、delay until_time |
| `triggertime` | 工作流觸發時間 | 記錄觸發時刻（與 nowTime 不同，延遲節點後兩者會有差異） |
| `triggeraid` | 觸發人帳號 ID | FieldPatch 中寫入發起人（注意：PersonRef 中用 `kind: "triggerUser"`，FieldPatch.value 中用 `kind: "systemField", fieldId: "triggeraid"`） |

### 佔位符語法（`$...$`）

以下場景統一使用 `$nodeAlias-fieldId$` 佔位符嵌入動態值：
- `kind: "template"` 的 `value`（通知正文、郵件主題等）
- `config.expression`（compute 數值公式）
- `config.offsetExpression`（compute 日期偏移表示式）

規則：
- `nodeAlias` 部分：引用觸發節點時按「觸發節點引用約定」使用實際別名或 nodeId
- `fieldId` 部分：必須是真實欄位 ID，嚴禁 alias
- **系統欄位**使用固定字首 `system`：`$system-nowTime$`、`$system-triggertime$`、`$system-triggeraid$`

### 各作用域下的記錄引用

| 作用域 | 引用當前記錄的 node | 說明 |
|---|---|---|
| 主流程 | 按「觸發節點引用約定」取得的實際別名或 nodeId | 詳見文件頂部 |
| 子流程內部 | `{ nodeAlias: "sub_trigger" }` | 固定別名，代表當前遍歷的那條記錄 |
| 審批塊內部 | `{ nodeAlias: "approval_start" }` | 固定別名，代表被審批的記錄 |

- **觸發記錄**：`{ kind: "record", node: <triggerNodeRef> }`
- **其他表記錄**：先用查詢節點（`get_single` / `get_multiple`）取得，再用查詢節點的 nodeAlias 引用
- **cc / approve / fill_in**：`config.target` 只支援單條記錄。多條時用 `sub_process`

> [!CAUTION]
> **跨作用域禁令（最常見的建置錯誤）**
>
> 子流程/審批塊是**獨立的封閉作用域**——內部節點**不能**引用外部主流程節點的資料，反之亦然。違反會導致 `nodeId not found` 或欄位靜默回傳空值。

**作用域可見性矩陣**（✅ 可引用 / ❌ 不可引用）：

| 當前位置 \ 引用目標 | 主流程節點 | 子流程內部節點 | 審批塊內部節點 | systemField |
|---|---|---|---|---|
| **在主流程中** | ✅ | ❌ | ❌ | ✅ |
| **在子流程中** | ❌ | ✅（含 `sub_trigger`） | ❌ | ✅ |
| **在審批塊中** | ❌ | ❌ | ✅（含 `approval_start`） | ✅ |

### 常見錯誤對照

| ❌ 錯誤寫法 | ✅ 正確寫法 | 原因 |
|---|---|---|
| `{ kind: "field", node: { nodeAlias: "start" }, fieldId: "triggertime" }` | `{ kind: "systemField", fieldId: "triggertime" }` | `triggertime` 是系統欄位，不屬於任何節點，不需要 `node` |
| 模板中寫 `$sub_trigger-nowTime$` | `$system-nowTime$` | 系統欄位在模板中必須用固定字首 `system`，不能用節點別名 |
| `{ kind: "field", node: { nodeAlias: "update_status" }, fieldId: "674...a1" }` | 引用觸發節點或上游查詢節點的 fieldId | `update_record` 節點無輸出欄位，引用會觸發 `StartNodeControlsIsNull` |
| 子流程內 `{ node: { nodeAlias: "start" } }`（主流程別名） | `{ node: { nodeAlias: "sub_trigger" } }` | 子流程不能跨作用域引用主流程節點，只能內部引用 |
| 審批內 `{ node: { nodeAlias: "start" } }`（主流程別名） | `{ node: { nodeAlias: "approval_start" } }` | 審批塊內部只能用固定別名 `approval_start` |
| `{ kind: "field", fieldId: "status" }` | `{ kind: "field", node: { nodeAlias: "..." }, fieldId: "674...a1" }` | `field` 必須攜帶 `node`；`fieldId` 必須用真實 ID，嚴禁 alias |

---

## 釋出流程

呼叫 `publish_process` 釋出工作流。參數：`appId` + `workflow_id`（即 processId）。

釋出前平台會自動做**完整校驗**（必填欄位、節點引用、分支路徑數 ≥ 2、審批塊至少含 1 個 approve 等）。校驗失敗 → 整體失敗，`error.code = PUBLISH_FAILED`，`error.message` 逐行列出各問題。

不含子流程/審批塊時，直接調 `publish_process`（`appId` + 主流程 `processId`）即可。

> [!CAUTION]
> **含子流程/審批塊時的釋出順序（違反必報 `NodeAppIsNull` 致命錯誤）**：
>
> 子流程/審批塊建立後，其內部流程初始狀態為**未釋出**。如果直接釋出主流程，會丟擲 `NodeAppIsNull` 致命錯誤。
>
> **正確流程**：建立內部節點後 → 調 `publish_process`（`appId` + 內部 `processId`）**立即釋出該子流程** → 所有子流程釋出成功後 → 調 `publish_process`（`appId` + 主流程 `processId`）**最後釋出主流程**。

## 錯誤恢復

`batch_create_process_nodes` 是**原子操作**——任一節點校驗失敗，整批都不會建立。

**`batch_create_process_nodes` 失敗時**：
1. 分析 `error.message` 定位出錯節點和原因（格式：`nodes[nodeAlias].config.xxx: 错误描述`）
2. 重新閱讀本 skill 定位違反的約束，修正該節點參數
3. 修正後**重新提交整批節點**

**`publish_process` 失敗時**（節點已建立但釋出校驗不透過）：
1. 從 `error.message` 逐行提取校驗問題，定位出錯節點
2. 調 `get_workflow_structure` 確認出錯節點及其所有下游節點
3. 對下游中的 `sub_process` / `approval_block` 節點，先調 `delete_process`（傳其內部 `processId`）清理內部流程，**避免孤兒流程**
4. 從鏈尾到出錯節點，逐個調 `delete_process_node` 刪除（平台會自動重連引用鏈，但順序刪可減少不必要的重連）
5. 修正參數後調 `batch_create_process_nodes` 重建出錯節點及下游節點（帶正確的 `prevNode` 鏈；含子流程/審批塊的需重新走兩步建立）
6. 重新發布：子流程內部節點出錯時需先發布子流程再發布主流程；主流程節點出錯時直接釋出主流程
