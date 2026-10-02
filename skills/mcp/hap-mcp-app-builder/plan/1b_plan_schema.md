# HapPlan JSON 結構規範

使用者已確認方案總覽後，按以下規則生成結構化 JSON，寫入 `hap-plan.json`。

> **⚠️ 格式紅線**：所有字串參數中，**禁止使用未轉義的英文雙引號 `"`**。若需引用文字，必須使用中文雙引號 `""` 或單引號 `''`。

---

## 頂層結構

```json
{
  "org_id": "来自 Step 0 选择的组织 ID",
  "appName": "应用名称",
  "appIcon": "图标名称，如 0_lego",
  "appColor": "主题色，如 #2196F3",
  "navLayout": "group | tree | top | card",
  "navColor": "appColor | white | gray | black",
  "enableExternalPortal": true,
  "worksheets": [],
  "worksheetViews": [],
  "worksheetCustomActions": [],
  "customPages": [],
  "workflows": [],
  "roles": [],
  "aiAssistants": [],
  "navGroups": []
}
```

### 屬性約束說明：
* **`org_id`**：組織 ID，鍵名必須使用下劃線風格 `org_id`，**嚴禁寫成駝峰 `orgId`**（MCP 工具參數名為 `org_id`）。
* **`appIcon`**：應用圖示，必須嚴格從 `plan/icon_and_style_guide.md` 中挑選契合業務語義的預設圖示。
* **`appColor`**：應用主題色，必須且只能使用 `plan/icon_and_style_guide.md` 中提供的 9 種官方高階 Hex 色值。**只有應用本身有顏色**，工作表、自訂頁面、AI 助手均無顏色屬性。
* **`navColor`**：導航欄顏色，若使用 `appColor` 代表導航欄使用應用主題色。
* **`enableExternalPortal`**：是否啟用外部門戶。`true` 表示啟用外部門戶（若規劃了外部門戶角色 `"roleScope": "externalPortal"`，此項必須為 `true`）；`false` 或不傳表示不啟用。

---

## 一、`worksheets`

每張工作表必須包含：
- `icon`：從 `plan/icon_and_style_guide.md` 中挑選最契合業務語義的圖示。不同工作表應儘量使用不同圖示，避免全部雷同
- `description`：一句話說明該表的業務定位與核心用途（如「記錄每一筆圖書借閱與歸還事件」）

### `fields`（緊湊字串陣列）

### 基本格式

1. 每個欄位用緊湊格式：`"字段名(Type)"`，如 `"任务标题(Text)"`、`"负责人(Collaborator)"`
2. 關聯欄位：`"字段名(Relation:目标工作表名)"`，如 `"关联图书(Relation:图书)"`
3. 自關聯：`"字段名(selfRelation)"`，如 `"上级分类(selfRelation)"`
4. **SingleSelect / MultipleSelect / Dropdown 必須攜帶選項值**，用 `/` 分隔：`"状态(SingleSelect:待处理/处理中/已完成/已逾期)"`。禁止只寫 `"状态(SingleSelect)"` 而不列選項
5. 必須充分利用專屬欄位型別：座標/定位 → `Location`，行政區劃 → `Region`，流水號 → `AutoNumber`，人員 → `Collaborator`，部門 → `Department`，手機號 → `PhoneNumber`，郵箱 → `Email`，金額/價格 → `Currency`，日期計算 → `DateFormula`（如"應還日期(DateFormula)"）。**嚴禁將這些欄位降級為 `Text` 或 `Number`**

### 欄位豐富度要求（核心）

> ⚠️ **欄位不夠豐富是最常見的設計缺陷。** Plan 階段輸出的欄位就是最終要建立的欄位清單，Build 階段不應大量補充。因此必須在此階段就輸出完整、豐富的欄位。

**最低欄位數量**：
- 主資料表（如客戶、圖書、商品、裝置）：**≥ 15 個欄位**
- 業務單據表（如訂單、借閱記錄、工單）：**≥ 12 個欄位**
- 過程/流水錶（如入庫單、巡檢記錄）：**≥ 8 個欄位**

**欄位維度覆蓋**：按 `plan/design_guide.md` 中「欄位完整性」的 7 個維度和「業務場景欄位補全」逐項檢查，確保每個維度至少覆蓋 1 個欄位，並根據業務場景主動補齊容易遺漏的欄位。

### `consistencyNotes`（必填）

每張表必須填寫欄位與檢視/工作流/自訂動作的一致性說明：
- 哪些 SingleSelect 欄位的哪些選項值支撐哪些檢視的篩選條件
- 哪些欄位會被工作流讀取或更新
- 自訂動作的前後狀態變化
- 示例：`"状态字段的已逾期选项用于超期事项视图筛选；点击处理按钮时状态须为待处理，工作流执行后更新为处理中；超期检查工作流自动将状态更新为已逾期"`

## 二、`worksheetViews`（獨立頂層陣列）

1. 每項包含 `worksheet`（工作表名稱）和 `views`（緊湊字串陣列）
2. 檢視格式：`"视图名(Type)"`，如 `"列表视图(Table)"`、`"看板视图(Kanban)"`
3. 為每張表優先生成 1～4 個最有業務價值的核心檢視
4. **檢視-欄位-工作流三方閉環**：所有檢視篩選條件和時效性狀態必須透過閉環檢查後才能提交

## 三、`worksheetCustomActions`（獨立頂層陣列）

1. 每項包含 `worksheet`（工作表名稱）和 `actions`（動作物件陣列）
2. 動作物件欄位：
   - `name`：動作名稱
   - `description`：由誰在什麼場景下點選，以及需要填寫什麼
   - `type`：`"updateCurrentRecord"` / `"createRelatedRecord"` / `"triggerWorkflow"`
   - `targetWorksheet`：僅 `type="createRelatedRecord"` 時填目標工作表名
   - `relateFieldName`：僅 `type="createRelatedRecord"` 時填，表示源工作表中用於物理關聯目標表的關聯欄位名稱（例如當前工作表中存在 `"关联商机(Relation:销售机会)"` 欄位，此處則必須填寫 `"关联商机"`）
   - `enableCondition`（可選）：按鈕的前置狀態條件，自然語言描述。有前置狀態要求的動作必填
   - `intentHints`：`type="triggerWorkflow"` 時必須填寫業務效果與約束陣列（`[{label}]`）

3. 只生成業務上真正需要**人工觸發**的動作
4. **型別自檢**：若 `updateCurrentRecord` 的所有欄位值均可由系統自動確定，則改為 `triggerWorkflow`
5. **審批自檢（嚴禁違反）**：嚴禁建立「審批透過」「審批駁回」「審批否決」等直接操作審批結果的自訂動作。正確做法：建立一個 `triggerWorkflow` 型別的動作（如「提交審批」「發起審批」），或透過新建記錄時自動觸發（`worksheet_event`），由工作流內部的審批業務塊 (`approval_block`) 來處理透過/駁回/填寫等流轉——透過與駁回由審批人在審批節點中操作，不是按鈕
6. **掛載自檢**：動作所在工作表必須是操作的**發起方**，而非目標表
7. **閉環自檢**：`createRelatedRecord` 必須有對應的目標工作表，且**必須確保源工作表與目標工作表之間已經顯式建立並宣告瞭關聯關係（Relation 欄位）**。大模型必須在動作的 `relateFieldName` 中指明具體的關聯欄位名稱，且該欄位必須在源工作表的 `fields` 清單中顯式存在。如果源表和目標表之間在規劃中沒有直接的關聯欄位，則禁止將其規劃為 `createRelatedRecord`，而應當：
   - (1) 在源工作表欄位清單中顯式追加並宣告 Relation 關聯欄位，並在 `relateFieldName` 中引用它；
   - (2) 或者將自訂動作的型別設計為 `triggerWorkflow`（透過後臺工作流在點選時自動建立對應記錄並建立資料同步）。
8. **欄位修改自檢**：`updateCurrentRecord` 必須有實際需要填寫的欄位。

## 四、`customPages[].components`（緊湊字串陣列）

1. 必須指定 `pageType`：`"dashboard"`（資料統計）或 `"workspace"`（工作臺）
2. `description`：一句話說明該頁面的業務目的與目標使用者（如「面向管理層的借閱資料全域統計看板」）
3. **圖示固定**：`dashboard` 固定使用 `"sys_control-panel_traffic"`，`workspace` 固定使用 `"2_3_statistics"`。無需從 icon guide 挑選
4. 元件格式：`"组件名(Type)"`
5. **命名規範**：元件名稱必須具體反映業務含義，嚴禁使用"按鈕1"、"業務分析"等模糊命名

**dashboard 頁面要求：**
- 固定包含 4 或 6 個 `NumberChart`，2～6 個業務圖表，1～2 個 `PivotTable`
- 每個圖表標註資料源：`"组件名(ChartType:工作表名)"`
- 禁止用維度表（分類表）作資料源，必須用事實表（訂單表）

**workspace 頁面要求：**
- 主要是 `Button`（4～6 個）和 `View`（2～4 個）
- 可輔以 `Text`、`Carousel`、`Section`
- 展示型推薦內容（如新書推薦、熱門商品、精選案例）應使用 `Carousel` 而非 `View`。

## 五、`workflows`

1. `description`：一句話說明該工作流的業務目標（如「借閱到期前 1 天自動提醒借閱人歸還」）
2. `trigger.type`：`worksheet_event` / `schedule` / `date_field`
2. `trigger.label`：觸發節點展示文字，如「借閱記錄新增時」
3. `trigger.source`：`worksheet_event` → 工作表名稱；`date_field` → `工作表名称（日期字段名）`；`schedule` → `""`
4. `intentHints` 是**業務效果與約束**陣列，不要寫成節點步驟：
   - ✅ `"通知内容应包含图书名称、作者、分类等关键信息"`
   - ❌ `"获取图书的书名、作者、分类信息"`
   - ✅ `"仅处理状态为借阅中的记录"`
   - ❌ `"查询所有借阅中的记录"`
   - **禁止引用具體欄位選項值**（如「全部借出」），只描述業務目標
5. **不輸出** `CustomAction` 觸發型別的工作流到此處，它們已內嵌在 `worksheetCustomActions` 的 `intentHints` 中

## 六、`roles`

角色物件下欄位：

- `name`：角色名稱
- `description`：一句話說明該角色的職責定位與權限範圍（如「負責日常借閱登記與歸還操作的前臺工作人員」）
- `roleScope`：角色型別。`"general"` = 組織內部角色（預設）；`"externalPortal"` = 外部門戶角色
- `permissions`：緊湊字串陣列，格式 `"名称(类型)"`，如 `"图书(worksheet)"`、`"运营看板(customPage)"`

## 七、`aiAssistants`

直接複用總覽「AI 助手」章節的內容；總覽中沒有時傳空陣列 `[]`。

1. `description`：一句話說明該助手的服務場景與能力範圍（如「幫助讀者查詢圖書庫存、推薦書目、解答借閱規則」）
2. **圖示固定使用 `"17_6_reddit"`**，無需從 icon guide 挑選

## 八、`navGroups`

1. 每個分組的 `items` 用緊湊格式：`"名称(worksheet)"`、`"名称(customPage)"`、`"名称(aiAssistant)"`
2. 所有工作表、儀表盤、AI 助手必須全部出現在某個分組中，**不遺漏**
3. 名稱必須與方案中定義的名稱**完全一致**

---

## ⚠️ 提交前閉環自檢

寫入 `hap-plan.json` 前必須檢查：
1. 每個檢視篩選條件是否有對應的欄位選項值
2. 每個時效性狀態選項是否有配套的自動標記工作流
3. 每個自訂動作的啟用條件是否完整
4. 每張表的 `consistencyNotes` 是否覆蓋了檢視篩選、工作流讀寫的關聯說明
5. `navGroups` 是否包含了所有工作表、自訂頁面和 AI 助手
6. **欄位豐富度**：每張主資料表是否 ≥ 15 個欄位、業務單據表 ≥ 12 個、過程表 ≥ 8 個
7. **7 維度覆蓋**：每張表是否覆蓋了主標識、核心業務屬性、狀態分類、時間、責任協作、數量金額、說明憑證 7 個維度
