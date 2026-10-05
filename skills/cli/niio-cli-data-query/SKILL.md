---
name: niio-cli-data-query
description: 用 niio CLI 命令列查詢/篩選/統計 niio 工作表裡的業務資料時用本 skill——尤其當篩選條件複雜、需要多條件 AND/OR、巢狀分組，或要做透視表聚合統計（求和/計數/平均/分組維度）。只要使用者說「查某張表裡滿足…條件的記錄」「按狀態/日期篩選資料」「這個篩選器怎麼寫」「統計每個月/每個分類的合計」「做個透視/彙總」，即使沒明說工具名也應觸發。不用於：寫入資料（增刪改記錄用 record 命令）。
---
> **對外表達規範**：對使用者的說明、提示與成果摘要，統一使用 niio 品牌及台灣繁體中文。執行所需的技術名稱、套件、命令、API 參數與路徑請保留；只在操作或除錯所需的程式碼中呈現，勿將它們用作產品標題或品牌名稱。


# niio 資料查詢助手（篩選 · 透視 · 統計）

幫使用者用 niio CLI 命令列從 niio 工作表裡**把想要的資料查出來**。難點不在命令本身，而在**參數 JSON 怎麼寫對**——篩選條件的寫法、各處支援哪些比較方式、透視的維度與聚合。本 skill 把這些易錯點講清楚，並給可直接套用的模板。

> 本 skill 只管"查/篩/統計"（只讀）。定位到目標行後要**寫回資料**（改備註、改狀態等）用
> `hap worksheet record update`——**寫記錄不依賴預設應用**，有 `WORKSHEET_ID` 就能定位，
> `-a/--app-id` 可傳可不傳（傳了只是限定欄位查詢範圍），寫入失敗時別往「是不是沒 select
> 對應用」上想。各欄位型別該傳什麼值見 `hap guide record`，寫完讀回確認。
> 增刪改記錄也直接用 `hap worksheet record` 相關命令。

## 覆蓋的命令

| 命令 | 用途 | 篩選器格式 |
| --- | --- | --- |
| `worksheet record list` | 按條件查記錄（篩選/排序/分頁） | **filter-json（統一篩選寫法）** |
| `worksheet record pivot` | 透視聚合（分組維度 + 求和/計數等） | **filter-json（同上）** |
| `worksheet record bottom-stats` | 檢視底部那條彙總（單行統計） | filter-controls（主站 wire，**不同**） |
| `worksheet record relations` | 順著某條記錄的關聯欄位列出被關聯的記錄 | 無（直接給 記錄+欄位） |
| `worksheet record logs` | 某條記錄的變更日誌（誰在什麼時候改了什麼） | 無 |
| `worksheet chart` | 圖表命令組（create/get/update/delete/list） | spec-json（在 `chart create` 上） |

> **關鍵認知**：`record list` 和 `record pivot` 共用同一套 **filter-json**；`bottom-stats` 用的是另一套老格式，別混。絕大多數"查資料"訴求用前兩個就夠。

## 第 0 步永遠是：拿到欄位 ID

篩選條件裡的 `field` 可以寫欄位 ID（controlId）、別名，或介面上顯示的列標題原文（工作表上沒有的名字會被點名拒絕）；
但透視的維度 `--rows-json` / `--columns-json` 和值 `--values-json` **只認欄位 ID 或別名**，寫列標題會被拒。先查出來：

```bash
hap worksheet fields WORKSHEET_ID        # 列出每個欄位的 controlId / 名稱 / 型別
```

記下要篩選/分組/聚合的那幾個欄位的 controlId，後面 JSON 裡直接用。

---

## filter-json：篩選器怎麼寫（record list / pivot 通用）

### 寫法

篩選條件就是一組條件，用 `logic` 組合，**可巢狀**以表達複雜的與/或：

```jsonc
{ "logic": "and",                     // and | or
  "items": [
    { "field": "<欄位 ID、別名或列標題>",
      "op": "<比較方式>",
      "value": <標量 或 陣列> },       // empty / not_empty 不需要 value
    { "logic": "or", "items": [ ... ] }  // 某一項本身也可以是一個組
  ] }
```

要表達「(A 且 B) 或 (C 且 D)」就在 `items` 裡再嵌組。這一種寫法 `hap` 各處都收——記錄查詢、檢視、
業務規則、按鈕、圖表、工作流條件——權威說明見 **`hap guide record filter`**（3.1 寫法、3.2 各處支援哪些
比較方式、3.3 透視的限制），它隨 CLI 版本走，別照本 skill 的記憶寫。

> 舊寫法（`{"type":"group","children":[{"type":"condition",...}]}` 那棵樹）和舊拼法（`notin`、`isempty`、
> `ge`、`startswith`…）仍然可用，以前寫的篩選照樣能跑；新寫的一律用上面這種。

### 比較方式：記錄查詢能用哪些

**`record list` / `record pivot` 能用這 21 個**：

```
eq ne  in not_in  contains not_contains  all_contains
starts_with not_starts_with  ends_with not_ends_with
gt gte lt lte  between not_between  belongs not_belongs
empty not_empty
```

檢視、業務規則、按鈕、圖表那幾處還多一些專用的比較方式（`date_is`、`self`、`rc_eq`、`array_eq`…），
**它們在 `record list` / `record pivot` 上不存在**——寫了 `hap` 會當場拒絕並列出這裡能用的。
各處的完整對照見 `hap guide record filter` 的 3.2。

要點：

- **日期也用 `between`**（配 `["2026-02-01","2026-03-31"]`）和 `gt` / `gte` / `lt` / `lte`。
  在檢視/規則/按鈕/圖表上，`hap` 會按列型別自動換成日期專用的比較方式，你照常寫即可；
  但 `date_between` 這類顯式日期名只在那幾處合法，**記錄查詢會拒絕它**。
- `empty` / `not_empty` **不帶 `value`**。
- 寫錯名字、寫了這裡沒有的比較方式、寫了不存在的列，`hap` 都會在發出去之前點名拒絕並告訴你可用取值。
- `node` 鍵和物件形態的 `value` 只屬於工作流條件，寫在記錄查詢裡會被拒絕。

> 🚨 **伺服器端對不認識的比較方式不報錯——它把整個條件丟掉，回傳全表，並且報成功。**
> 用一個它不認的名字去查十二條逾期訂單，拿回來的是全部訂單，沒有任何跡象說明篩選沒生效。
> 你能看到報錯，靠的是 `hap` 在發出去之前的本地攔截。所以**只要不是用 `hap` 發的篩選請求
> （自己拼 HTTP、別的客戶端），看結果要看條數，別隻看 `success`。**

### value 怎麼填（按欄位型別）

- **選項 / 單選 / 多選欄位**：value 用選項的 **key** 最穩（從 `worksheet fields` 的欄位 options 裡查）；寫選項的顯示文字 `hap` 也會替你換成 key。
- **關聯表欄位（Relation）**：value 用關聯記錄的 **rowid 陣列**，配 `in` 或 `eq`。⚠️ 必須用 rowid，**不能用關聯顯示的標題文字**（如版本名）去匹配。怎麼拿這個 rowid 見下方「關聯欄位篩選」。子表的反向關聯欄位同理：value 填**父記錄的 rowid**，即可篩出該父記錄的全部子行。
- **成員欄位（Collaborator）**：value 用成員的 **accountId 陣列**，配 `in`/`eq`。
- **部門欄位**：value 用部門 **ID 陣列**，配 `belongs` / `not_belongs`（在 `record pivot` 上這兩個只對**地區**欄位可用，見下方 pivot 一節）。
- **文字欄位**：`contains` / `starts_with` / `eq` 等，value 直接給文字。
- **日期欄位**：`between` 給 `["2025-01-01","2025-01-31"]`，或 `gt` / `gte` / `lt` / `lte` 給單個日期/時間戳（**不是** `date_between`，記錄查詢不收它）。

### 關聯欄位篩選：先拿到關聯記錄的 rowid

關聯欄位（如「任務」表裡的「版本」「專案」「客戶」）在**回傳資料里長這樣**——一個陣列，每項帶 `sid`（關聯記錄的 rowid）和 `name`（顯示標題）：

```json
"版本欄位": [ { "sid": "ITERATION_ROW_ID", "name": "迭代A" } ]
```

篩選時 value 要用那個 `sid`。**最直接的辦法是讓命令替你列**：

```bash
hap --json worksheet record relations <本表WS_ID> <本條記錄rowid> <關聯欄位ID>
```

它順著這條記錄的關聯欄位把被關聯的記錄列出來，並附帶它們的來源工作表資訊——省掉下面兩步手工反查。
分頁用 `-p`/`-n`（預設每頁 20），要連繫統欄位一起拿加 `--is-return-system-fields`。

手工反查的兩種辦法（還沒有具體某條記錄、或要按名字找時用）：

1. **從關聯表查**：去被關聯的那張表 `record list --search "迭代A"`，拿到目標記錄的 `rowid`。注意關聯顯示的 `name` 來自該表的標題欄位，可能和你以為的不一樣（比如標題其實是 "2.3" 而非 "迭代A 2.3"），所以以實際查到的為準。
2. **從已有資料反查**：先 `record list` 拉幾條本表記錄，看那個關聯欄位裡已出現的 `{sid, name}`，挑出 `name` 匹配的 `sid`。

拿到 sid 後這樣篩（任務表裡「版本」關聯到「迭代A」）：

```bash
hap worksheet record list TASK_WS_ID --filter-json '{
  "logic":"and",
  "items":[{"field":"<版本欄位ID>","op":"in","value":["ITERATION_ROW_ID"]}]
}' -p 1 -n 100
```

#### 子表（SubTable）：查"某條父記錄下的所有子行"

子表資料不在父記錄裡，存在一張獨立工作表（父 SubTable 欄位的 `dataSource`），
子行透過**反向 Relation 欄位**（父 SubTable 欄位的 `sourceField`）掛回父行。
所以查某父記錄的子行 = 在子表工作表上，按這個反向關聯欄位篩 = 父記錄 rowid：

```bash
hap worksheet record list <子表WS_ID> --use-field-id-as-key -p 1 -n 100 \
  --filter-json '{"logic":"and","items":[
    {"field":"<反向關聯欄位ID>","op":"in","value":["<父記錄rowid>"]}]}' \
  --sorts-json '[{"field":"<明細編號等排序欄位ID>","isAsc":true}]'
```

- `<反向關聯欄位ID>`：在父表 `worksheet fields` 裡，找 SubTable 欄位的 `sourceField`。
- value 是**父記錄的 rowid**（不是父記錄標題文字），用 `in`。
- 子錶行的"第幾行"由排序決定，通常按 AutoNumber 明細編號升序，與表單裡看到的順序一致；
  務必帶 `--sorts-json`，否則預設順序不保證穩定，"數第 N 行"會數錯。


### 完整示例

「姓張、且 1 月入職」**或**「在銷售/市場部、或屬於華北區」：

```bash
hap worksheet record list WORKSHEET_ID --filter-json '{
  "logic": "or",
  "items": [
    { "logic": "and", "items": [
      { "field": "name",         "op": "starts_with", "value": "張" },
      { "field": "onboard_date", "op": "between",     "value": ["2025-01-01","2025-01-31"] }
    ]},
    { "logic": "or", "items": [
      { "field": "dept_option",  "op": "in",      "value": ["k_sales","k_mkt"] },
      { "field": "dept_id",      "op": "belongs", "value": ["DEPT_HUABEI_ID"] }
    ]}
  ]
}'
```

簡單單條件（狀態為空的記錄）——注意 `empty` 不帶 value：

```bash
hap worksheet record list WORKSHEET_ID --filter-json '{
  "logic":"and",
  "items":[{"field":"status","op":"empty"}]
}'
```

---

## record list：查記錄

```bash
hap worksheet record list WORKSHEET_ID \
  --filter-json '<見上>' \
  --sorts-json '[{"field":"onboard_date","isAsc":false}]' \
  --fields '["name","status","amount"]' \   # 只回傳這幾個欄位，省 token
  --page-size 50 --page-index 1 \
  --include-total-count                       # 想要總行數時加
```

- `--page-size` / `--page-index` **都是必填**。
- `--search` 關鍵字模糊搜尋（跨欄位），可與 filter 疊加。
- `--view-id` 套用某檢視的內建篩選/排序。
- 不傳 `--filter-json` 就是查全部（按分頁）。
- **回傳資料預設用欄位別名作 key**（如 `mingcheng`、`fuzeren`、`ssdd`），不是 controlId。所以解析結果時按別名取值，或加 `--use-field-id-as-key` 讓 key 變成 controlId。別名可在 `worksheet fields` 裡看到。
- `--fields` 傳欄位 ID 或別名都行；只想要某幾列時用它省 token。
- 成員欄位回傳的是物件陣列 `[{accountId, fullname, avatar, status}]`，取 `fullname` 顯示人名。

---

## record pivot：透視聚合（統計的首選）

任何「按 X 分組，算 Y 的合計/計數/平均」都用它。**只有 `--values-json` 是必填**；`--view-id` 可選
（給了就套用該檢視的篩選/排序，檢視 id 用 `hap worksheet view list WORKSHEET_ID` 查），
`-p`/`-n` 不傳走預設值。`-a` 也可以不傳——命令會按工作表反查它屬於哪個應用；傳錯了會明確告訴你
「這張表不屬於該應用，請用它真正所屬的應用」。

```bash
hap worksheet record pivot WORKSHEET_ID \
  --view-id VIEW_ID \                                          # 必填
  --rows-json '[{"field":"status"}]' \                         # 行維度（分組）
  --columns-json '[{"field":"create_date","granularity":3}]' \ # 列維度，可選
  --values-json '[{"field":"amount","aggregation":"SUM"}]' \   # 值（聚合），必填
  --filter-json '<同 list 的篩選條件>' \                        # 可選
  --include-summary                                            # 要總計行加
```

回傳結構是 `data.pivot`（一個陣列），每項形如：

```json
{ "rows":    { "<行維度欄位ID>": "進行中" },
  "columns": { },
  "values":  { "<值欄位ID>": 190000.0 } }
```

解析時按欄位 ID 從 `rows`/`values` 裡取值；要排名就把 `pivot` 陣列按某個 value 排序後取前 N（透視本身不保證按值排序）。

### 🚨 pivot 能用的篩選比 list 少

同一份 filter-json，`record list` 收、`pivot` 未必收——**pivot 認哪些比較，取決於欄位裝的是什麼**：

| 比較方式 | 在 pivot 上 |
| --- | --- |
| `eq` / `ne`、`empty` / `not_empty` | 都行 |
| `contains` / `not_contains` | **一律不行**，任何欄位型別都拒。`hap` 本地就攔下並提示改用 `starts_with` / `ends_with`，或乾脆換 `record list` |
| `in` / `not_in` | 只在**單選、地區**上行；文字 / 數值 / 日期會被拒 |
| `gt` / `gte` / `lt` / `lte`、`between` / `not_between` | 只在**數值、日期**上行 |
| `belongs` / `not_belongs` | 只在**地區**上行 |
| `all_contains` | 只在**文字**上行 |
| `starts_with` / `ends_with` 及其否定式 | 只在**文字**上行 |

除 `contains` 外，其餘按型別的限制 `hap` 攔不住（它不知道欄位型別），由伺服器端拒絕並把你這次發的
條件補回錯誤資訊裡，形如「A pivot accepts fewer comparisons than `record list` does…」。

**pivot 還挑 `value` 的形態**（`record list` 不挑，兩種寫法都收）：

| 比較方式 | pivot 要什麼 |
| --- | --- |
| `gt` / `gte` / `lt` / `lte` | **裸值**。寫成陣列會被拒——`"value": 0` 行，`[0]` 和 `["0"]` 都不行 |
| `between` / `not_between` | **兩個元素的陣列**。寫成裸值、或只給一個元素，都會被拒 |
| `eq` / `ne` / `in` / `not_in` | 兩種都收，不用管 |

同一條件在 `record list` 上無論哪種寫法都能跑，**所以這類報錯只會在換成 pivot 時冒出來**。
這兩張表以 `hap guide record filter` 的 3.3 為準。

> 篩不動就退回 `record list` 拿明細，再在本地聚合——比跟 pivot 的型別和形態限制較勁快。

### 維度（rows / columns）

每項 `{"field":"<controlId 或別名>", "displayName":"可選", "granularity":<整數>, "includeEmpty":false}`：

- `granularity` 僅對**日期/地區**欄位有意義：
  - 日期：`1`=日，`2`=周，`3`=月
  - 地區：`1`=省，`2`=省/市，`3`=省/市/縣
- `includeEmpty`：是否把空值也作為一組，預設 false。

### 值（values）

每項 `{"field":"<controlId 或別名>", "aggregation":"<聚合>", "displayName":"可選"}`：

- `aggregation`（不區分大小寫）：`COUNT` 計數、`DISTINCTCOUNT` 去重計數、`SUM` 求和、`MIN` 最小、`MAX` 最大、`AVG` 平均。
- **只想數行數**（不針對某欄位）：`field` 填特殊值 `record_count`，配 `COUNT`。

示例——按月統計每個狀態的訂單數和金額合計：

```bash
hap worksheet record pivot WORKSHEET_ID \
  --rows-json '[{"field":"create_date","granularity":3}]' \
  --columns-json '[{"field":"status"}]' \
  --values-json '[
    {"field":"record_count","aggregation":"COUNT"},
    {"field":"amount","aggregation":"SUM"}
  ]' --include-summary
```

---

## bottom-stats 與 chart（次要）

- **`record bottom-stats`**：只回傳檢視底部那一行彙總（不是多維透視）。它走的是**另一套老格式**：`--column-rpts '[{"controlId":"amount","rptType":1}]'`（rptType 是整數，按 `--help` 確認對應關係），`--filter-controls` 用主站 wire 結構而非 filter-json。另有 `-k/--keywords` 按關鍵字篩，以及 `--report-id`——給了它就讀**某個圖表檢視**的彙總而不是普通表格的彙總（圖表 id 來自 `hap worksheet chart list`）。需要真正的分組統計時優先用 `record pivot`。
- **`record logs`**：某條記錄的變更日誌，回答"這個值是誰什麼時候改的"。定位到可疑記錄後用它，比翻應用級 `hap app logs` 精準。
- **`worksheet chart`**：**是一個命令組**（`create` / `get` / `update` / `delete` / `list`），
  在工作表上建/改圖表設定，不是即時取數。建圖用 `hap worksheet chart create`，
  `--report-type`（整數圖表型別）+ `-j/--spec-json`（含 xaxes/yaxisList/filter 等）都在**子命令**上，
  `hap worksheet chart --help` 只會列出子命令。圖表規格怎麼寫見 `hap guide chart`。
  建圖表多數時候屬於"改應用"，可交給 niio-cli-app-editor；純取數分析用 `record pivot` 更直接。

先看 `hap worksheet record bottom-stats --help` / `hap worksheet chart create --help` 再用。

---

## 寫對查詢的要點

照這些規則寫，絕大多數查詢一次就成：

- **欄位標識**：篩選條件裡的 `field` 可用 controlId、別名或列標題；透視的維度 / 值裡只認 controlId 或別名（用 `worksheet fields` 查）。
- **篩選條件**：統一寫法 `{"logic","items":[{"field","op","value"}]}`，比較方式用 `gte` / `lte` / `empty` / `not_in` 這類統一名；檢視/圖表專用的（`date_is`、`self`…）記錄查詢不收。拿不準就看 `hap guide record filter`。
- **value 形態**：選項欄位用選項 key；關聯欄位用關聯記錄 rowid；成員欄位用 accountId；`empty` / `not_empty` 不帶 value。
- **必填項**：只有 `record pivot` 的 `--values-json` 是必填。分頁 `-p`/`-n` 都有預設值
  （`record list` 每頁 20、`pivot` 每頁 100，頁碼都從 1 起），`--view-id` 兩個命令都是可選的。
  要一次取更多就顯式給 `-n`。
- **結果解析**：回傳預設用欄位別名作 key，要用 controlId 作 key 就加 `--use-field-id-as-key`；成員/關聯欄位是物件陣列，取其中的 `fullname` / `name`。
- **Shell 轉義**：用單引號包整個 JSON、內部用雙引號；篩選複雜時寫進檔案再 `--filter-json "$(cat f.json)"`。
- **核對實際請求**：`hap config log on` 後再跑命令，可在日誌裡看到真正發出的請求體。
