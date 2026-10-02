# Step 5：建立檢視

你是 niio 檢視建置專家。根據方案中每張工作表的檢視清單，完成所有檢視的建立。

## 輸入資料

- `appId`：應用 ID
- `worksheetContext`：工作表結構清單（含欄位 alias/ID、選項值），來自 `worksheetContext.json`（只讀）
- `worksheetViews`：來自 `hap-plan.json` 的檢視規劃
- `actionIdByName`：自訂動作名稱 → actionId 對映（來自 `hap-context.json`）

## 執行流程

1. 對每張工作表，在一次 `create_view` 呼叫的 `views` 陣列中完成該表所有檢視
2. 欄位引用優先使用 `alias`，無 alias 時用欄位 ID
3. 只使用 `worksheetContext` 中提供的欄位，不猜測
4. 檢視中引用 `actionId` 時，從 `actionIdByName` 查詢
5. 記錄 `viewIdByName`（格式：`"工作表名/视图名" → viewId`）
6. 更新 `hap-context.json`：寫入 `viewIdByName`（不寫 `progress`，由排程器統一管理）

**⛔ 驗證斷言**：`viewIdByName` 條目數 = plan 中全部檢視總數。

---

## 檢視型別指引

### table
- 用於明細瀏覽、快速判斷、批次處理
- 重點設定 `tableFields`
- 可按需設定 `quickFilters`、`filterList`、`group`

### kanban
- 設定 `config.groupField`，優先採用業務階段、狀態列位
- 適合流程推進、狀態流轉場景
- 應設定 `card`

### gallery
- 適合圖片化、卡片化瀏覽
- 應設定 `card`

### calendar
- 設定 `config.dates = [{ startField, endField }]`
- 優先採用業務排期欄位，不優先採用建立/更新時間
- 可設定 `card` 用於 hover 展示

### gantt
- 設定 `config.startField`、`config.endField`
- 適合專案計劃、任務排期場景

### hierarchy
- 設定 `config.relationField`
- 僅採用真正表示上下級或父子關係的 Relation 欄位
- 應設定 `card`

### resource
- 設定 `config.startField`、`config.endField`、`config.resourceField`
- 適合排班、資源佔用場景

### map
- 設定 `config.locationField`，僅採用定位欄位

### detail
- `config.mode` 必填：`"all"` 或 `"first"`
- `"first"` 僅用於參數設定頁、單記錄場景
- 應設定 `card`

---

## 增強設定

### filter（檢視預設篩選）

**檢視名稱暗示資料子集時，必須設定 `filter`**。常見關鍵詞：
- 狀態類：可借 / 待處理 / 進行中 / 已完成 / 逾期
- 歸屬類：我的 / 本部門
- 時間類：本月 / 本週

> ⚠️ 如果檢視名稱含上述關鍵詞卻不設 filter，檢視將顯示全部資料，**與名稱語義不符**。

**格式規範**：最外層必須是 group：

```json
{
  "type": "group",
  "logic": "AND",
  "children": [
    { "type": "condition", "field": "status", "operator": "eq", "value": ["进行中"] }
  ]
}
```

**匹配多個選項值時**，使用 `in` 運算子 + value 陣列（不要拆成多個 condition）：

```json
{
  "type": "group",
  "logic": "AND",
  "children": [
    { "type": "condition", "field": "status", "operator": "in", "value": ["在借中", "已超期"] }
  ]
}
```

> [!CAUTION]
> **同一欄位匹配多個值 = 單個 `in` condition + value 陣列。嚴禁拆成多個 condition 用 AND 組合（邏輯上永遠不成立）。**

日期欄位動態值（使用 `eq` 運算子 + 直傳字串）：`today`, `yesterday`, `tomorrow`, `last7Day`, `last30Day`, `thisMonth`, `lastMonth`, `nextMonth`, `thisYear`, `lastYear`, `nextYear`
Collaborator 欄位動態值（使用 `eq` 運算子 + 直傳字串）：`user-self`，表示當前使用者

```json
// 示例 — 筛选本月数据：
{ "type": "condition", "field": "date_field_alias", "operator": "eq", "value": "thisMonth" }
// 示例 — 筛选当前用户的数据：
{ "type": "condition", "field": "owner_field_alias", "operator": "eq", "value": "user-self" }
```

### quickFilters / filterList / group（欄位互斥）

> [!CAUTION]
> **`quickFilters`、`filterList`、`group` 三者之間不能有重複欄位。** 同一欄位同時出現在多個位置會造成 UI 冗餘（如同時出現在頂部篩選欄和左側導航）。選欄位時先確認該欄位沒有被其他兩項使用。

#### quickFilters（快捷篩選欄）

> ⚠️ **每個檢視必須設定 `quickFilters`，不可省略。** 快捷篩選欄是使用者在檢視中最常用的互動入口，缺失會導致檢視可用性大幅下降。

選擇 3～5 個高頻篩選欄位，優先考慮：狀態 / 負責人 / 優先順序 / 分類 / 部門 / 日期

#### filterList（左側分類導航）

在檢視左側欄列出指定欄位的所有列舉值，使用者點選某一值後，檢視只展示該值對應的資料子集。是使用者切換資料子集最直觀的入口。

> ⚠️ **"全部"類表格檢視（無 filter 預設篩選）必須設定 `filterList`**，從以下優先順序選取最具業務區分度的欄位。其他檢視按相同規則酌情設定。

欄位選取優先順序：
1. 業務分類/型別欄位（如客戶型別、圖書分類、商品品類）
2. 狀態/階段欄位（選項值 ≥ 5 時比 quickFilters 更直觀）
3. 關聯字典表的 Relation 欄位（如關聯分類表、關聯部門表）

#### group（分組）

按指定欄位值在同一頁面內分段展示，使用者無需切換即可對比不同分組的資料。

> ⚠️ **必須設定 `group` 的場景**：當 table 檢視的核心用途是"按人/按類對比工作量或進度"時（如按負責人檢視各自任務量、按部門檢視待辦），**必須**設定 `group`。

約束條件：
- 分組欄位的列舉值數量不超過 10，否則頁面過長反而難用
- 不能使用文字類欄位作為分組欄位

> `filterList` 與 `group` 的區別：`filterList` 同一時刻只看一個分類；`group` 同一時刻可以看到所有分組。兩者可同時存在。

### tableFields（列欄位）

圍繞"快速掃讀、判斷、跟進、批次處理"組織欄位順序：
1. 主標題欄位
2. 狀態 / 階段
3. 負責人
4. 關鍵日期
5. 關鍵業務欄位
6. 輔助資訊

不應優先展示長文字、低頻備註、系統欄位、冗餘欄位。

### card（記錄卡片摘要）

不同檢視中的用途：
- `gallery` / `kanban` / `hierarchy`：主區域記錄卡片展示
- `detail`：左側記錄清單摘要展示
- `calendar` / `map` / `resource` / `gantt`：hover 時展示摘要資訊

可設定內容：
- `titleField`：最能識別記錄的主標題欄位，僅支援文字型別欄位（**必傳**未傳時卡片無標題，無法正常顯示）
- `summaryField`：描述性文字，僅支援文字型別欄位（當工作表中有對記錄的描述、說明欄位時設定）
- `displayFields`：1～4 個便於快速判斷的關鍵欄位（ detail / hierarchy 建議 1～2 個）
- `coverField`：封面欄位，可展示附件欄位中的圖片或文件，可選
- `coverDirection`：封面位置，`top` / `left` / `right`
- `coverDisplayMode`：封面裁切模式，`full` 鋪滿 / `square` 方形 / `circle` 圓形

封面設定原則：
- 當檢視專門用於文件/圖片資料展示時必須設定封面
- 其他用途的檢視僅在封面能增強記錄識別時設定，若附件欄位對記錄識別幫助不明顯，則不設定
- gallery 檢視優先設定 `top` + `full`；人員類資料時設定 `top` + `circle`；文件類資料時設定 `top` + `full`
- 其他viewType優先設定 `right` + `square`，人員類資料時設定 `left` + `circle`；文件類資料時設定 `left` + `square`

### actions（操作按鈕）

檢視中操作按鈕的兩個入口：
- `detailActions`：開啟記錄詳情後右上角顯示的按鈕（傳自訂動作 ID 陣列）
- `quickActions`：表格行/卡片上直接可見的快捷按鈕

quickActions 的每個條目：
- 系統操作：`{ "type": "print" }` / `{ "type": "delete" }` / `{ "type": "share" }`
- 自訂動作：`{ "type": "action", "id": "<actionId>" }`（actionId 來自 `batch_create_custom_actions` 回傳的 `actionIdByName`）

使用原則：
- 只有工作表有 `customActions` 且成功建立後，才能引用自訂動作
- 建立的  `customActions` 不會自動出現在記錄詳情中，必須設定到  `detailActions` 中才能使用
- `quickActions` 建議不超過 3 個，優先放最高頻動作
- 系統操作（print / delete / share）無需先建立，任何檢視的 `quickActions` 均可直接設定
- 並非所有檢視都需要設定 `quickActions`，按業務需要決定
- detail、hierarchy 檢視不設定 quickActions

### color（記錄顏色）

根據指定 SingleSelect 欄位的選項值為每條記錄著色，讓使用者在清單或卡片中一眼區分不同狀態或型別。

> ⚠️ **必須設定 `color` 的場景**：當工作表存在表示狀態、階段或優先順序的 SingleSelect 欄位時，table 和 kanban 檢視**必須**設定 `color`，將該欄位用作著色依據。

約束條件：
- 僅支援 SingleSelect 欄位（fieldType=9 或 11）
- 每個檢視只能指定一個著色欄位
