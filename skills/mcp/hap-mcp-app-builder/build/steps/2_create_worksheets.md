# Step 2：建立工作表

你是 niio 工作表建置專家，負責將方案中的所有工作表建立完畢。

## 輸入資料

- `appId`：應用 ID
- `worksheetToSectionId`：工作表名 → sectionId 的對映（從 `hap-context.json` 的 `sectionIdByName` 推導）
- `worksheets`：所有工作表的規劃清單（來自 `hap-plan.json`）

## 執行流程

按依賴順序逐張建立工作表：

1. 先建被引用表（無關聯依賴的主資料表），再建引用方（含 Relation 欄位的業務表）
2. 每張表呼叫 `create_worksheet`，傳入對應的 `sectionId`、`icon`、`color`，以及 `remark`、`desc`、`importantNote` 等參數（參數規則見下方）
   - **`icon` 和 `color` 必須原樣使用 plan 中該工作表的值，嚴禁自行替換或編造**
3. 固定設定 `createDefaultView: false`（預設檢視在後續步驟單獨建立）
4. 記錄回傳的 `worksheetId`，存入 `worksheetIdByName[表名]`
5. 更新 `hap-context.json`：寫入 `worksheetIdByName`（不寫 `progress`，由排程器統一管理）

**⛔ 驗證斷言**：`worksheetIdByName` 條目數 = plan 中工作表數量，每個值均為 24 位物理 ID。

---

## 欄位控制屬性

| 屬性 | 適用型別 | 說明 |
|---|---|---|
| `isTitle` | Text / AutoNumber | 每張表**僅一個**欄位可設為 true（標題欄位），其他控制元件不支援作標題，否則建表失敗 |
| `required` | 大多數 | 必填。**注意**：AutoNumber / Formula / Collaborator / Divider **不可設為 true**，否則建表失敗 |
| `isReadOnly` | 大多數 | 只讀 |
| `isUnique` | Text / Number / Email / PhoneNumber 等 | 唯一約束 |
| `isHiddenOnCreate` | 任意 | 新建記錄時是否隱藏（如系統自動寫入的欄位）|
| `precision` | Number / Currency / Formula | 小數位（0-14）|
| `max` | Rating | 最大評分值（1-10）|


## 工作表參數規則

### remark（必填）

面向開發者/AI 的工作表描述。根據 plan 中該工作表的 `description`，生成一句簡潔的描述，說明該表的業務定位與核心用途。

### desc（必填）

面向使用者的工作表使用說明，在標題旁顯示幫助圖示，hover 時顯示；當同時設定了 importantNote 時，desc 變為"詳情"連結展開顯示（**必須使用原生 HTML + 行內 CSS 編寫，禁止使用 Markdown**）。每張表都應生成一段簡明的使用指南，根據表的業務特徵涵蓋以下要點（按實際情況裁剪，不硬湊）：

- 該表的核心用途和適用場景（這張表管什麼、誰來用）
- 資料的生命週期或流轉路徑（如"新建 → 稽核 → 歸檔"）
- 當有 importantNote 時，desc 中應包含其**詳細說明**：哪些欄位由系統/工作流自動維護、具體觸發條件是什麼等，作為 importantNote 一句話警告的展開補充

### importantNote（按需生成）

顯示在工作表標題下方的重要提示文字（始終可見）。**大部分表不需要設定**——當表存在以下典型場景時才設定，否則留空：

- 表中包含由工作流/系統自動更新的狀態列位 → 提醒"狀態列位由系統自動維護，請勿手動修改"
- 表的資料依賴其他表的前置資料（如報銷單需先有關聯專案）→ 提醒"請先在專案表中建立對應專案"
- 表涉及審批流程（從 plan 工作流方案推斷）→ 提醒"提交後將進入審批流程，請確認資訊無誤後再提交"

- `importantNoteColor`：固定使用 `"#515151"`（深灰）

### createDefaultView（固定 false）

固定設定為 `false`，禁止自動建立預設檢視。檢視在後續步驟（Step 5）中單獨建立和設定。

---

## 欄位設計規範

> [!CAUTION]
> **Plan 欄位屬性不可變原則**：plan 中已明確定義的欄位屬性——**名稱、型別、選項值、關聯目標表**——是不可修改的，執行器必須原樣使用。執行器只能在此基礎上**補充** plan 未定義的設定（Divider 分段、layout 佈局、alias、placeholder、remark、defaultValue、config 等），以及**追加** plan 中遺漏的欄位。嚴禁篡改已有欄位的名稱、型別或選項值。

### 一、建表前的業務思考

在保留 plan 中所有欄位的前提下，主動擴充套件上下游與治理欄位：

| 欄位類別 | 典型欄位 |
|---|---|
| 狀態/階段 | 狀態、處理階段 |
| 優先順序/重要度 | 優先順序、緊急程度 |
| 歸屬與協作 | 負責人、協作者、所屬部門 |
| 時間維度 | 計劃開始/結束、截止日期、實際完成 |
| 分類/標籤 | 分類、標籤、型別 |
| 治理 | 是否歸檔、是否啟用、審批結果 |
| 附件/備註 | 附件、備註、說明 |

### 二、標題欄位（isTitle）

每張工作表**有且僅有一個**標題欄位。選擇規則：

- 優先選**識別度最高的 Text 欄位**（如"名稱"、"標題"）
- 僅以下型別可設為標題：`Text`、`AutoNumber`
- **禁止**把人員(`Collaborator`)、部門(`Department`)、定位(`Location`)、附件、關聯、富文字(`RichText`)、單選/多選等控制元件設為標題——niio 會以「標題欄位控制元件型別不支援」拒絕建表（`__fatal_error__`，整次造應用中止）

> 如果 plan 中沒有顯式指定標題欄位，自行判斷並設定。**若表內沒有上述可作標題的欄位（例如全是人員/選項/關聯類欄位），必須新建一個 Text 欄位作為標題欄位**，不要退而求其次選非法型別。

### 三、欄位型別決策

```
單選 ≤ 5 個選項 → SingleSelect
單選 > 5 個選項 → Dropdown
多選 ≤ 10 個選項 → MultipleSelect
多選 > 10 個選項 → Dropdown
單個是/否 → Checkbox（不要用 SingleSelect + 是/否）
人員 → Collaborator（不要用 Text 替代）
電話 → PhoneNumber，郵箱 → Email，金額 → Currency
流水號 → AutoNumber，計算值 → Formula
日期差/時長計算 → DateFormula（如工齡、逾期天數、專案週期）
```

### Date / DateTime / Time 顯示格式（必須）

Date / DateTime / Time 欄位必須顯式傳 `config.format`，採用 Moment.js 格式符號（**注意：與 AutoNumber 的 .NET 格式不同，不要混用**）。根據使用者語言選擇符合其地區習慣的年月日順序和分隔符（如中文用"年月日"、美式用 `MMM D, YYYY`、歐式用 `D MMM YYYY`）。精度可按業務需要裁剪（僅年、年月、年月日、帶時分、帶秒均可）。無法判斷時用 ISO 格式 `"YYYY-MM-DD"` 兜底。

> ⚠️ **唯一易錯點**：大寫 `D` = 日，小寫 `d`/`dd`/`ddd` = 星期。寫反會顯示異常。排班、日程、考勤等場景建議追加 `ddd`。

常用模板：
- 中文日期：`"YYYY年M月D日"`，帶時間：`"YYYY年M月D日 HH:mm"`，帶星期：`"YYYY年M月D日 ddd"`
- 英文日期：`"MMM D, YYYY"`，帶時間：`"MMM D, YYYY HH:mm"`，帶星期：`"ddd, MMM D, YYYY"`
- ISO 兜底：`"YYYY-MM-DD"`，帶時間：`"YYYY-MM-DD HH:mm"`
- 僅年：`"YYYY"`，年月：`"YYYY-MM"` / `"YYYY年M月"`
- 純時間：`"HH:mm"`（預設），僅小時：`"HH"`，含秒：`"HH:mm:ss"`

### alias 生成規則

每個欄位必須設定 `alias`，命名約定：
- 全域唯一字首 `biz_`
- 字尾由欄位語義對應的英文短片語成（snake_case），如 `biz_visitor_name` / `biz_visit_time` / `biz_status`
- 不要重複，同表內 alias 必須唯一

### required 約束

AutoNumber、Formula、Divider **不得設定** `required: true`，否則工作表建立會失敗。

### Formula 引用規則

Formula 的 `expression` 中引用其他欄位必須用 `$alias$` 包裹，不能用 `name`。先確定所有欄位 alias，再寫 expression。

示例：`"$biz_total_amount$ * (1 - $biz_discount_rate$)"`

### AutoNumber 常用模板

- 純流水號：`[{ type: "sequence", length: 6, repeat: "never" }]`
- 日期 + 流水：`[{ type: "createdTime", format: "yyyyMMdd" }, { type: "sequence", length: 4, repeat: "day" }]`
- 字首 + 流水：`[{ type: "text", value: "ORD-" }, { type: "sequence", length: 6, repeat: "never" }]`

### 選項值解析規則

Plan 中的 SingleSelect / MultipleSelect 欄位攜帶選項值，格式為 `"字段名(SingleSelect:选项1/选项2/选项3)"`。建表時：

1. **必須使用 Plan 中指定的選項值**，不要自行增減或改名——檢視篩選和工作流依賴這些確切的選項名
2. 解析示例：`"状态(SingleSelect:待处理/处理中/已完成/已逾期)"` → options: `[{value:"待处理"}, {value:"处理中"}, {value:"已完成"}, {value:"已逾期"}]`
3. 如果 Plan 中未攜帶選項值（只寫了 `"状态(SingleSelect)"`），則根據業務語義自行補全

### 四、Divider 分段規範

每張表都應使用 Divider 分組欄位，分段名必須結合業務語義生成：

- 先按欄位語義分組，再提煉分段名
- 名稱簡潔自然，通常 2～6 個字，優先使用業務詞
- 每張表建議 2～5 個 Divider，每組建議 3～8 個欄位
- 附件、備註、說明、歸檔類內容放最後

禁止使用空泛模板名：`基本信息`、`归属与协作`、`计划与进度`、`审批与治理`、`备注与附件`

應根據業務內容自然命名：
- 客戶表：`客户资料`、`联系信息`、`跟进情况`
- 合同表：`合同主体`、`签约安排`、`履约信息`

Divider 固定屬性：`required: false`，`layout: { rowIndex: N, span: 12 }`（N 按當前行號遞增）

### 五、Layout 佈局規則

每個欄位的 `layout` 必須同時傳 `rowIndex`（行號，從 0 開始遞增）和 `span`（列寬）。

> [!CAUTION]
> **只有 `rowIndex` 相同的欄位才會顯示在同一行。** `rowIndex` 不同則一定分行，與欄位陣列順序無關。同一行內各欄位的 `span` 之和必須 = 12。

#### span 取值

**只允許三種值：3 / 6 / 12，禁止使用 4、8。**

| 每行欄位數 | span | 說明 |
|---|---|---|
| 1 個欄位獨佔 | 12 | 獨佔一行 |
| 2 個欄位同行 | 6 | 兩個欄位設相同 rowIndex |
| 4 個欄位同行 | 3 | 四個欄位設相同 rowIndex |

❌ 不允許一行 3 個欄位（span:4）

#### rowIndex 分配示例

```json
// Divider 独占一行
{ "alias": "div_basic", "type": "Divider", "layout": { "rowIndex": 0, "span": 12 } }
// 两个字段并排
{ "alias": "biz_name",   "layout": { "rowIndex": 1, "span": 6 } }
{ "alias": "biz_code",   "layout": { "rowIndex": 1, "span": 6 } }
// 四个字段同行
{ "alias": "biz_phone",  "layout": { "rowIndex": 2, "span": 3 } }
{ "alias": "biz_email",  "layout": { "rowIndex": 2, "span": 3 } }
{ "alias": "biz_date",   "layout": { "rowIndex": 2, "span": 3 } }
{ "alias": "biz_number", "layout": { "rowIndex": 2, "span": 3 } }
// 独占一行
{ "alias": "biz_remark", "layout": { "rowIndex": 3, "span": 12 } }
```

#### 強制獨佔一行的欄位型別

Divider、RichText、Attachment、Relation（displayMode 為 inlineTable / tabTable 時）→ 必須 `span: 12`，獨佔一個 `rowIndex`。

> Relation（displayMode=dropdown/card）時可與其他欄位並排，其中 dropdown 推薦 span=3/6，card 推薦 span=6/12。

#### 語義成組（同行並排）

緊湊欄位（dropdown、Number、Currency、Date、PhoneNumber、Email、AutoNumber）優先 4 個一行（span:3，相同 rowIndex）；僅當語義上天然成對時才 2 個一行（span:6）。

span:3 示例（優先）：
- 數量 + 單價 + 金額 + 折扣率
- 聯絡電話 + 郵箱 + 入庫日期 + 編號

span:6 示例（語義成對）：
- 開始時間 + 結束時間
- 狀態 + 優先順序
- 負責人 + 所屬部門

### 六、選項顏色規則

狀態/階段/優先順序類欄位必須加顏色：
- 負面/失敗/拒絕 → `#F52222`（紅）
- 正面/完成/透過 → `#00C345`（綠）
- 警告/待處理 → `#FAD714`（黃）
- 進行中 → `#2D46C4`（藍）
- 取消/歸檔 → `#484848`（灰）

純分類/標籤欄位不加顏色。

可選顏色集：`#C0E6FC #C3F2F2 #00C345 #FAD714 #FF9300 #F52222 #EB2F96 #7500EA #2D46C4 #484848`

### 七、Relation 欄位規範

#### 參數設定
每個 Relation 欄位必須同時包含 `dataSource`、`config.bidirectional`、`config.displayMode` 三個屬性。`displayMode` 非 `dropdown` 時，`config.showFields` 不得為空。

- **`dataSource`**（欄位頂層屬性，非 config 內）
  - 填目標表的真實 worksheetId（從 `worksheetIdByName[targetWorksheet]` 查）
  - 自關聯填 `"selfRelation"`
  - **嚴禁**自行編造 ID，嚴禁從 plan 中直接複用任何 ID 值

- **`config.bidirectional`** → 始終設為 `true`

- **`config.displayMode`**（必填，嚴禁省略）

根據業務場景從下表選擇：

| displayMode | 適用場景 | 對應表型別 | 備註 |
|---|---|---|---|
| `dropdown` | 關聯目標是**字典/分類/標籤表**（資料源表），僅選擇引用、無需展示詳情 | 如 `图书类型`、`客户级别`、`任务状态` | 條目少、結構簡單 |
| `card` | 關聯目標是**核心業務表**（實體表），需展示關鍵欄位（**預設推薦**） | 如 `图书清单`、`订单`、`客户`、`项目` | 可設 coverField |
| `inlineTable` | 多條記錄、需直接檢視/操作 | 子表式業務明細（如 `订单明细`） | 適合子表式展示 |
| `tabTable` | 大量記錄、需獨立管理 | 一對多且量大（如 `操作日志`） | 放在表單最末尾 |

- **`config.showFields`**（條件必填）

  - `displayMode` 為 `card` → **必須 ≥ 2 個**，推薦 2-4 個
  - `displayMode` 為 `inlineTable` / `tabTable` → **必須 5-10 個**
  - `displayMode` 為 `dropdown` → 不需要

取值：目標表中最具業務識別度的欄位 alias（從 plan 中目標表的欄位清單挑選，轉為 `biz_` 開頭的 alias）

- **`config.coverField`**（條件必填）
  - 僅 `displayMode=card` 時有效
  - 當目標表有附件欄位，且該附件是記錄的核心視覺標識（如產品圖、頭像、封面圖、證件照、Logo）時必須設定
  - 以下場景**不設** coverField（因為這些附件不是記錄的視覺身份，顯示為縮圖無辨識意義）：
    - 操作性截圖（如 bug 截圖、巡檢拍照）
    - 純文件類附件（如合同 PDF、報告、表格）
    - 輔助性附件（如簽名、回執）

#### 目標表未建好時的處理
  - 若目標表尚未建好 → **跳過整個 Relation 欄位**
  - 目標表建表時會設定 `bidirectional: true`，API 自動在本表建立反向關聯欄位

#### Relation dataSource 取得流程

```
plan 字段有 targetWorksheet（目标表名）
  ↓
targetWorksheet == "selfRelation"
  ↓ 是 → dataSource = "selfRelation"
  ↓ 否 → 查 worksheetIdByName[targetWorksheet]
            ↓ 找到 → 填入 dataSource，设 bidirectional: true
            ↓ 未找到 → 跳过该 Relation 字段
```

### 八、預設值（defaultValue）規範

#### 何時設定

預設值用於減少重複填寫、提升錄入效率。只有欄位存在明確、穩定、可預期的初始值時，才建議設定。

優先在以下場景設定預設值，其他場景按需判斷：

| 場景 | 做法 |
|---|---|
| 負責人欄位 → 預設為當前操作使用者 | `source: "system", value: "currentUser"` |
| 建立日期 → 預設為今天 | `source: "system", value: "now"` |
| 狀態列位 → 有明確的初始狀態（如"待處理"） | `source: "static", value: "待处理"` |
| 同一表單中的欄位值 → 預設取當前表單內其他欄位的值 | `source: "field", field: "startTime"` 示例：結束時間 → 預設為開始時間；收貨地址 → 預設為定位欄位；發貨數量 → 預設為採購數量 |
| 選擇關聯記錄後 → 自動帶出該關聯記錄中的欄位值 | `source: "relation", relationField: "customer", field: "phone"` 示例：選擇"客戶"後，自動帶出該客戶的"聯絡電話"填入當前表單；選擇"主任務"後，預設帶出"主任務"的"負責人"、"截止日期"等 |

#### 使用規則
- system：用於系統內建值，如當前使用者、當前時間
- static：用於固定值，如狀態預設"待處理"
- field：用於當前表單內其他欄位的值
- relation：用於已選關聯記錄中的欄位值

#### 原則
- 優先用於高頻、重複、規則明確的填寫場景
- 應以減少輸入成本為目標，不應增加誤填風險
- 不確定、易變化、依賴人工判斷的欄位，不建議設定預設值

#### 格式

始終傳陣列；單值欄位只放一個物件：

```json
"defaultValue": [
  { "source": "system", "value": "currentUser" }
]
```

#### 各欄位型別支援範圍

| 欄位型別 | 多值 | static | system | field/relation |
|---|---|---|---|---|
| Text | ✅ | ✅ | — | ✅ |
| Number / Currency | — | ✅ | — | ✅ |
| SingleSelect | — | ✅(選項名) | — | ✅ |
| MultipleSelect / Dropdown | ✅ | ✅ | — | ✅ |
| Date / DateTime | — | ✅(YYYY-MM-DD HH:mm:ss) | `now` | ✅ |
| Collaborator / Department | config.isMultiple | — | `currentUser` | ✅ |
| Role | config.isMultiple | — | — | ✅ |
| PhoneNumber / Email | — | ✅ | `currentUser` | ✅ |
| LandlinePhone | — | ✅ | — | ✅ |
| Region | — | — | — | ✅ |
| Rating | — | ✅(數字) | — | ✅ |
| Location | — | — | `currentLocation` | ✅ |

> AutoNumber / Formula / Attachment / Relation / Divider 不支援 defaultValue。

### 九、欄位輔助文字規範

#### placeholder（必填）

所有輸入型欄位**必須設定 placeholder**，引導使用者瞭解應輸入什麼內容。

支援的欄位型別：`Text`、`Number`、`Email`、`PhoneNumber`、`LandlinePhone`、`Dropdown`、`Date`、`DateTime`、`Time`、`Currency`

| 欄位型別 | placeholder 示例 |
|---|---|
| Text（名稱類） | "請輸入客戶全稱" |
| Text（描述類） | "請簡要描述問題現象和影響範圍" |
| Number | "請輸入數量" |
| PhoneNumber | "請輸入手機號" |
| Email | "請輸入郵箱地址" |
| Date/DateTime | "請選擇日期" |
| Dropdown | "請選擇" |

#### desc（按需生成）

面向使用者的欄位輸入說明，顯示在欄位下方。當欄位有**特別的填寫要求**或**選項含義需要解釋說明**時生成：

- 欄位有格式要求、精度要求、業務規則等 placeholder 無法承載的資訊 → 用 desc 補充，**不重複** placeholder 已表達的內容
- 選項欄位（SingleSelect/MultipleSelect）的選項含義不直觀、需要使用者理解區別時 → 用 desc 解釋各選項的適用場景
- 不支援 placeholder 的欄位（如 Relation、Rating 等）有特殊操作要求時 → 用 desc 引導
- Checkbox 欄位勾選/不勾選的業務含義不明顯時 → 用 desc 說明勾選代表什麼
- Formula / AutoNumber 等只讀欄位 → 用 desc 解釋計算邏輯或編號規則，幫使用者理解顯示值

示例：金額欄位 → "含稅金額，精確到分"；關聯欄位 → "選擇本次服務對應的客戶"；Checkbox → "勾選表示已確認收貨"；公式欄位 → "由系統根據 單價×數量 自動計算"

> **禁止**生成僅重複欄位名稱的 desc（如欄位"性別"→ desc"請選擇客戶性別"），這類無額外資訊的 desc 不如不設。

#### remark（必填）

面向開發者/AI 的欄位註釋。build 階段**必須為每個欄位生成**，用一句話描述欄位的業務用途（如"記錄客戶首次聯絡日期，用於計算客戶生命週期"、"關聯訂單表，用於回溯採購來源"）。如果欄位被工作流讀寫或被檢視篩選依賴，應一併註明。
