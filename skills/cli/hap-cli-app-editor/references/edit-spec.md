# edit-spec 總覽

一個 edit-spec 是一個 JSON 檔案，描述對**一個已存在應用**的一組「讀改寫」式區域性修改。它只覆蓋三類編輯——**欄位、頁面元件、動作按鈕**——因為這三類的安全寫法是「讀出整體 → 改一處 → 整體寫回」，由 `hap app-editor` 替你完成。其他元素（工作表、檢視、角色、工作流、節點、應用與分組）直接用對應的 `hap` 命令，見各模組文件。

## 信封

```json
{
  "app": "<appId 或 应用名>",
  "org": "<组织 id，可选；默认当前会话组织>",
  "ops": [ { "type": "...", "...": "..." } ]
}
```

- `app`：優先用真實 appId；也可用應用名（命令會在當前組織裡解析）。
- `ops`：按宣告順序執行。同一 spec 內後面的 op 可引用前面 op 剛建立的元素。

## op 通用欄位

| 欄位 | 說明 |
|---|---|
| `type` | 必填，`<元素>.<动作>`，決定用哪份模組 schema 校驗。 |
| `confirm` | 破壞性 op（`field.delete` / `component.delete`）必填且必須為 `true`，否則拒絕執行。 |
| `label` | 可選，plan/apply 輸出裡顯示的人類標籤。 |

## 引用元素的方式

元素一律用**邏輯名**（工作表名、欄位名、元件名…）或**真實 id** 引用——兩者都行。命令每步執行前從
niio 即時讀取結構來解析。

**二級分組裡的工作表現在也解析得到。** 應用的分組樹會被整棵拍平（子分組一併納入），所以
`"worksheet": "<放在子分组里的表名>"` 不會再答「worksheet not found」，`inspect` 也會把它列出來。

- 工作表：`"worksheet"` 可以寫表名，也可以寫 **worksheetId**——名字在兩個分組裡重名時用 id 最穩。
- 分組：除了名字和 id，還可以寫**路徑** `"组/子组"` 來區分同名分組。

## op 總表

| type | 作用 | 詳見 |
|---|---|---|
| `field.add` | 新增欄位（增量，保留反向控制元件） | [worksheets-and-fields.md](worksheets-and-fields.md) |
| `field.update` | 改欄位（讀全量 → 改目標 → 整表寫回） | 同上 |
| `field.delete` | 刪欄位（整表寫回，需 confirm） | 同上 |
| `field.reorder` | 重排欄位（整表寫回） | 同上 |
| `component.add` | 頁面加元件（頁面佈局讀改寫） | [custom-pages.md](custom-pages.md) |
| `component.update` | 改頁面元件 | 同上 |
| `component.delete` | 刪頁面元件（需 confirm） | 同上 |
| `custom-action.create` | 新建動作按鈕（高層 action_spec 翻譯） | [custom-actions.md](custom-actions.md) |
| `custom-action.update` | 原地改動作按鈕 | 同上 |

寫了不在表裡的 `type`（比如 `view.update`、`node.add`），`validate` 會直接報錯並給出應該改用的 `hap` 命令。

> op 的欄位級 schema 在 `scripts/editspec/`（envelope + field + component + custom-action 各一份）。
> 這四份是 **niio CLI 同名檔案的副本**，放在這裡只為方便離線查閱；真正做校驗的是 CLI 內建的那份，
> 兩者不一致時**以 CLI 內建的為準**（`hap app-editor validate` 的結果就是權威答案）。

## 命令

```bash
hap app-editor validate <edit-spec.json>                 # 本地校驗，零網路
hap app-editor plan     <edit-spec.json> [--app <id>]    # dry-run 預演
hap app-editor apply    <edit-spec.json> [--app <id>] [--continue]  # 執行
hap app-editor inspect  <appId|名称> [--org-id <org>]    # 列印即時 名→id 結構
```

`inspect` 回傳 `app_id` / `org_id` / `name` / `sections` / `worksheets` / `pages_and_chatbots` /
`roles` / `workflows`；每張工作表帶著它所屬的 `section`，**含二級分組裡的表**。

`--app` 覆蓋 spec 裡寫的目標應用；`--continue` 讓某個 op 失敗後繼續跑剩下的（預設停）。

## field 的跨表塊（`field.add` 的欄位詞彙）

`field` 接受這些鍵：`name`、`type`、`required`、`unique`、`options`，加下面四個跨表塊，
再加 `control` 逃生口。**跨表型別必須帶自己那個塊**——少了會校驗報錯，不會建出一列指向為空的壞列。

| 塊 | 用在哪種型別 | 形狀 |
|---|---|---|
| `relation` | 關聯記錄（RELATE_SHEET / 29） | `{worksheet, multiple?, showFields?}` |
| `lookup` | 他表欄位（SHEET_FIELD / 30） | `{via, field}` |
| `rollup` | 彙總（SUBTOTAL / 37） | `{via, field}` |
| `formula` | 數值公式（FORMULA_NUMBER / 31）、日期公式（FORMULA_DATE / 38） | 字串表示式，**不是物件** |
| `subtable` | 子表（SUB_LIST / 34） | `{fields: [...]}` 新建，或 `{worksheet, showFields?}` 掛載——二選一 |

```json
{ "type": "field.add", "worksheet": "订单",
  "field": { "name": "客户", "type": "RELATE_SHEET",
             "relation": { "worksheet": "客户", "multiple": true,
                           "showFields": ["客户名称", "等级"] } } }

{ "type": "field.add", "worksheet": "订单",
  "field": { "name": "客户等级", "type": "SHEET_FIELD",
             "lookup": { "via": "客户", "field": "等级" } } }

{ "type": "field.add", "worksheet": "客户",
  "field": { "name": "订单总额", "type": "SUBTOTAL",
             "rollup": { "via": "订单", "field": "金额" } } }

{ "type": "field.add", "worksheet": "订单",
  "field": { "name": "含税金额", "type": "FORMULA_NUMBER",
             "formula": "$<金额字段id>$ * 1.06" } }
```

### 名字都能寫，由引擎解析成 id

- `relation.worksheet` 寫目標表的**名字或 id**；`relation.showFields` 寫目標表上那些列的
  **名字或 id**。
- `relation.multiple`：`true` 多條、`false` 單條（預設單條）。
- `lookup` / `rollup` 的 `via` 是**本表**上那根橋——關聯列或子表列，名字或 id 都行；
  `field` 是**遠端表**上要映象 / 要聚合的那一列。`via` 會被自動包成 `$<id>$` 的形態，
  不用自己寫美元號。
- **一個例外**：遠端表不在本應用裡（或不在導航裡、讀不到）時，`field` **只能寫 id**——
  引擎讀不到那張表就沒法把名字翻成 id，這時寫名字會報錯。
- `formula` 的表示式裡引用列一律用 `$<列id>$`（列 id 用 `hap worksheet fields` 取）。

### 校驗會擋住什麼

- **塊放錯型別**：`Field 'x' is a Number, so it cannot carry a 'relation' block.`
- **塊內未知鍵**：`ops[0].field.relation.bidirectional: unexpected property` ——
  `relation` 塊只有 `worksheet` / `multiple` / `showFields` 三個鍵，**沒有 `bidirectional`**。
  要雙向，先用 `relation` 塊建出來再 `hap worksheet pair-relation` 補反向端。
- **跨表型別缺塊**：`Field 'x' needs a 'relation' block saying what it points at.`
- **公式型別缺表示式** / **表示式放在非公式型別上**：都會明確報錯。
- `lookup` / `rollup` 的 `via` 指向的列**不通向另一張表**時，會告訴你「沒有東西可讀」。
- **子表 `fields` 與 `worksheet` 都給**：`ops[0].field.subtable: 'fields' and 'worksheet' cannot
  both be given; give exactly one` —— **在 `validate` 階段就被拒**。
- **子表兩者都不給**：`ops[0].field.subtable: give exactly one of: 'fields', 'worksheet'` —— 同樣
  在 `validate` 階段。
- **內聯模式帶了 `showFields`**：`The sub-table on field 'x' lists 'showFields' alongside new
  columns. The inline list shows the columns you are creating; 'showFields' is for picking among
  the columns an existing worksheet already has.`
- **`SUB_LIST` 完全沒有 `subtable` 塊**：`Field 'x' is a sub-table, so it needs a 'subtable' block
  saying what it holds.`

#### 哪些在 `validate` 就拒，哪些要等 `plan`

`validate` 只跑 schema（零網路），能擋住形狀問題；型別與塊的搭配要等 `plan`/`apply` 時的降級才發現。
所以**看到 `edit-spec OK` 不等於這份 spec 能跑**，動手前多跑一次 `plan`。

| 問題 | 誰攔下的 |
|---|---|
| 塊內未知鍵（如 `relation.bidirectional`、`subtable.allowadd`） | `validate` |
| 子表兩種模式都給 / 都不給 | `validate` |
| 塊放錯型別（Number 帶 `relation` / `subtable`） | `plan`（validate 報 OK） |
| 跨表型別缺塊、公式型別缺表示式 | `plan`（validate 報 OK） |
| 內聯子錶帶 `showFields` | `plan`（validate 報 OK） |
| `via` 不通向另一張表、遠端列名解析不了 | `plan`（要讀線上結構） |

帶了 `control` 逃生口的欄位不受「缺塊」這條攔阻（假定你自己在原始鍵裡寫全了），
且 `control` **最後合併、優先生效**。

### 子表有兩種模式，必須二選一

```json
// 模式一：新建一张子表，直接写它的列
{ "type": "field.add", "worksheet": "订单",
  "field": { "name": "订单明细", "type": "SUB_LIST",
             "subtable": { "fields": [
               { "name": "商品", "type": "Text", "required": true },
               { "name": "数量", "type": "Number" },
               { "name": "所属客户", "type": "RELATE_SHEET",
                 "relation": { "worksheet": "客户" } }
             ] } } }

// 模式二：把一张已存在的表挂成子表
{ "type": "field.add", "worksheet": "订单",
  "field": { "name": "维修记录", "type": "SUB_LIST",
             "subtable": { "worksheet": "维修单",
                           "showFields": ["故障描述", "处理人"] } } }
```

- **子欄位用與頂層 field 完全相同的 clean 形**——`name` / `type` / `required` / `unique` /
  `options`，而且**子欄位裡還能再寫 `relation` / `lookup` / `rollup` / `formula` 塊**，名字解析
  照樣生效（上例裡子欄位的 `relation.worksheet: "客户"` 會被解析成客戶表的 id）。不必學第二套詞彙。
- **`showFields` 只能用在掛載模式**：內聯模式下那些列還不存在，內聯清單顯示的就是你正在建的這些列。
  寫在內聯模式裡會被明確拒絕。掛載模式下 `showFields` 寫子表上那些列的名字或 id，不給就是全部可見列。
- `subtable.worksheet` 同樣接名字或 id。

兩種模式走的是不同的寫入路徑，值得知道：

| 模式 | 怎麼落地 |
|---|---|
| 內聯 `fields` | **整表寫回**（和 `field.update` / `field.delete` 同一條路）：讀出父表全部控制元件，把新的子表列接在後面，整份存回。同時建出一張承載子行的子表工作表。 |
| 掛載 `worksheet` | 與 `hap worksheet mount-subtable` **同一個兩步握手**：先建 SUB_LIST 列，再在子表側配好回指父表的反向關聯列。少了第二步，子錶行就不會按父記錄過濾顯示。 |

掛載完兩側都能讀到：父表的 SUB_LIST 列 `dataSource` 指向子表、`sourceControlId` 是子表側那根反向列；
子表上多出一列指回父表的關聯。子表工作表**不能單獨讀**，要 `hap worksheet fields <子表ID> --parent <父表ID>`。

**「恰好一個」是 schema 硬約束**：`fields` 和 `worksheet` 同時給、或兩個都不給，
`hap app-editor validate` 階段（零網路）就會拒絕：

```
兩者都給 → ops[0].field.subtable: 'fields' and 'worksheet' cannot both be given; give exactly one
都不給   → ops[0].field.subtable: give exactly one of: 'fields', 'worksheet'
```

## 這個引擎繼承哪些修復

`app-editor` 直接呼叫 CLI 的核心層，**不經過命令層**。所以命令層的行為（選項翻譯、參數推導、
確認提示）與它無關：命令列上加的新選項，不會自動出現在 edit-spec 裡。反過來，核心層的寫入規則
（整表寫回保反向控制元件、選項值校驗、按鈕填寫模式推導）它都拿得到。

一處例外要記住：`custom-action.create` / `custom-action.update` 裡**給 `config` 是原始逃生口，
不經介面卡**——填寫模式推導、門控、二次確認一概不生效。詳見
[custom-actions.md](custom-actions.md) 末節。

## 示例

```json
{
  "app": "myAppId",
  "ops": [
    { "type": "field.add", "worksheet": "订单",
      "field": { "name": "优先级", "type": "SingleSelect", "options": ["高", "中", "低"] } },
    { "type": "field.update", "worksheet": "订单", "field": "金额",
      "set": { "required": true } },
    { "type": "field.delete", "worksheet": "订单", "field": "废弃备注", "confirm": true },
    { "type": "component.add", "page": "首页",
      "component": { "name": "公告", "type": "richText", "value": "<p>本周盘点</p>" } }
  ]
}
```
