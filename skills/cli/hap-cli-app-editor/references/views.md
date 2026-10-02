# 檢視（view）— 命令參考與資料字典

檢視命令都掛在 `hap worksheet view <动词>` 下。機器可讀輸出在 `hap` 後加全域性 `--json`。

> **全域性規則：改複雜值前先用讀命令匯出現狀，在真實結構上改，再寫回。**

## 呼叫正規化

### 讀：list / info

```bash
# 列出工作表下的所有视图（拿 viewId / viewType / 名称）
hap --json worksheet view list 6845f0a1b2c3d4e5f6a7b8c9

# 找回删掉的视图（带删除时间）
hap --json worksheet view list 6845f0a1b2c3d4e5f6a7b8c9 --deleted

# 单个视图完整配置：filters、排序、显示字段、advancedSetting 全在这里
hap --json worksheet view info 6845f0a1b2c3d4e5f6a7b8c9 64a1b2c3d4e5f60123456789
```

任何「改複雜值」的操作（filters / fastFilters / navGroup / advancedSetting 裡的 JSON 串…）
都必須先 `view info` 匯出現狀，在真實結構上改，再寫回 —— 不要憑記憶手搓整個結構。

### 建立：create

```bash
# 默认表格视图
hap worksheet view create 6845f0a1b2c3d4e5f6a7b8c9 "全部订单"

# 看板：按某个选项/关联字段分组
hap worksheet view create 6845f0a1b2c3d4e5f6a7b8c9 "按状态" \
  --view-type board --group-control ctrl_status_24hex

# 画廊：附件字段做卡片封面
hap worksheet view create 6845f0a1b2c3d4e5f6a7b8c9 "产品图册" \
  --view-type gallery --cover-control ctrl_photo_24hex --cover-type 0

# 日历 / 甘特
hap worksheet view create 6845f0a1b2c3d4e5f6a7b8c9 "排期" \
  --view-type gantt --begin-date ctrl_start_24hex --end-date ctrl_end_24hex

# 层级：单表自关联树
hap worksheet view create 6845f0a1b2c3d4e5f6a7b8c9 "任务树" \
  --view-type structure --child-type 1 --group-control ctrl_parent_24hex

# 过滤表格（每个状态一张表）
hap worksheet view create 6845f0a1b2c3d4e5f6a7b8c9 "进行中" \
  --view-type sheet --filter-json '{"logic":"and","items":[{"field":"ctrl_status_24hex","op":"eq","value":"opt_key_1"}]}'
# ↑ 筛选条件用统一写法，见 `hap guide record filter`；旧的 wire 扁平数组（[{"controlId","dataType","spliceType","filterType","values"}]）仍然可用

# 一次成型整视图（分组/封面/过滤/快筛/筛选列表/行色/按钮）用 --view-spec，见 §0
hap worksheet view create 6845f0a1b2c3d4e5f6a7b8c9 "总览" --view-spec @view.json

# 其它创建期参数（advancedSetting 等）走逃生口
hap worksheet view create 6845f0a1b2c3d4e5f6a7b8c9 "紧凑表" \
  --config-json '{"advancedSetting":{"alternatecolor":"1"}}'
```

### 更新：update（區域性更新，三件套）

`view update` 是**區域性**更新：只有 `--edit-attrs` 列出的頂層屬性會被寫入，其餘保持原樣。

```bash
# 仅改名（最简形态，--edit-attrs 自动按 name 处理）
hap worksheet view update 6845f0a1b2c3d4e5f6a7b8c9 64a1b2c3d4e5f60123456789 \
  --name "看板（新）"

# 改 advancedSetting 子键 —— 必须三者配对：
#   --view-json 给值 + --edit-attrs 含 advancedSetting + --edit-ad-keys 列出改动子键
hap worksheet view update 6845f0a1b2c3d4e5f6a7b8c9 64a1b2c3d4e5f60123456789 \
  --view-json '{"advancedSetting":{"alternatecolor":"1","titlewrap":"1"}}' \
  --edit-attrs advancedSetting \
  --edit-ad-keys alternatecolor,titlewrap

# 改分组字段（看板分组 / 层级父字段 / 日历主时间字段都叫 viewControl）
hap worksheet view update 6845f0a1b2c3d4e5f6a7b8c9 64a1b2c3d4e5f60123456789 \
  --view-json '{"viewControl":"ctrl_owner_24hex"}' \
  --edit-attrs viewControl

# 改卡片显示字段及顺序（先 info 读出现有数组再整体替换）
hap worksheet view update 6845f0a1b2c3d4e5f6a7b8c9 64a1b2c3d4e5f60123456789 \
  --view-json '{"displayControls":["ctrl_a","ctrl_b"],"controlsSorts":["ctrl_a","ctrl_b"]}' \
  --edit-attrs displayControls,controlsSorts
```

坑位提示：

- **advancedSetting 必須配對 `--edit-ad-keys`。** 只給 `--edit-attrs advancedSetting`
  不給 `--edit-ad-keys`，等於讓服務端把整個 advancedSetting 當作改動範圍——
  沒出現在 `--view-json` 裡的其它子鍵可能被清掉。永遠把改了哪幾個子鍵顯式列出來。
- **advancedSetting 的值全部是字串**（布林寫 `"1"`/`"0"`，數字也寫成字串，
  JSON 結構先序列化成字串再放進去）。寫成裸數字/布林可能不生效。
- `--edit-attrs` 之外的鍵即使出現在 `--view-json` 裡也不會被寫入；反過來，
  列進 `--edit-attrs` 卻沒給值的屬性會被寫空。兩邊要一致。
- `filters` / `fastFilters` / `navGroup` / `viewControls` 這類陣列屬性是**整體替換**，
  務必先 `view info` 讀全量，在其上增刪，再整體寫回。

### 刪除 / 複製 / 排序

```bash
hap worksheet view delete 6845f0a1b2c3d4e5f6a7b8c9 64a1b2c3d4e5f60123456789 -y

# 复制（可选给新名字）—— 复杂视图调参前先 copy 一份当沙盒
hap worksheet view copy 6845f0a1b2c3d4e5f6a7b8c9 64a1b2c3d4e5f60123456789 "看板-副本"

# 视图在导航栏的顺序 = 传入 viewId 的顺序（要列全）
hap worksheet view sort 6845f0a1b2c3d4e5f6a7b8c9 \
  64a1b2c3d4e5f60123456789 64a1b2c3d4e5f6012345678a 64a1b2c3d4e5f6012345678b
```

> 檢視編輯**只走上面這些命令**——edit-spec 沒有 view 類 op，寫了會被 `validate` 拒絕並提示改用對應命令。檢視名 → viewId 用 `hap worksheet view list` 解析。

## 資料字典

字典核對於 hap-cli 0.9.0

### 0. `--view-spec` 高層方言

`view create --view-spec` / `view update --view-spec` 用的是一份**高層 JSON**，與下面 §2/§3 的
wire 層鍵名不是一回事：高層方言由 CLI 翻譯成 `editAttrs` + `advancedSetting`。要一次描述完整
檢視就用它，要位元組級控制某個設定項才下沉到 §2/§3。`view update --view-spec` 裡寫到的都會更新，
沒寫的保持原樣。欄位一律用 controlId 引用。

```jsonc
{
  "viewType": "gallery",
  "config": {"mode": "all"},                 // 详情视图：all 常规多条 / first 只看第一条
  "card": {
    "titleField": "<字段ID>",
    "coverField": "<附件字段ID>",
    "coverDirection": "top",                 // top | left | right
    "coverDisplayMode": "rectangle"          // rectangle | circle | full（square 是 rectangle 的旧写法）
  },
  "sort": [{"fieldId": "<字段ID>", "sortType": 1}],   // 1 升序 / 2 降序
  "quickFilters": ["<字段ID>"],
  "filterList": ["<字段ID>"],                 // 左侧导航分类，只能给一个字段
  "color": "<单选字段ID>",
  "tableFields": ["<字段ID>", "..."],
  "rowHeight": 0,                             // 0 紧凑 / 1 中等 / 2 高 / 3 超高
  "filter": {"logic":"and", "items":[
    {"field":"<状态字段ID>", "op":"eq", "value":"<选项key>"}
  ]}
}
```

#### 🚨 兩種「分組」是完全不同的兩件事

寫錯位置會被直接拒絕：

- **看板 / 層級 / 地圖 / 資源**：分組是**維度**（按哪個欄位分成列），但**四種檢視各讀各的 config 子鍵**，
  寫錯鍵會被靜默忽略：看板 `config.groupField`、層級 `config.relationField`、地圖 `config.locationField`、
  資源 `config.resourceField`。（命令級簡寫 `view create --group-control` 不走這些鍵，它直接寫 wire 的
  `viewControl`，四類都通用。）
- **表格 / 畫廊**：分組是**顯示方式**（把行按某欄位收攏成一段段），寫在**頂層 `groupBy`**。

```jsonc
{"viewType": "kanban", "config": {"groupField": "<状态字段ID>"}}                      // 看板
{"viewType": "sheet", "groupBy": {"fieldId": "<负责人字段ID>", "ascending": true}}    // 表格
```

`groupBy` 只能用在表格和畫廊上，用在看板上會報錯讓你改用它自己的分組欄位。

#### 幾個取值不要猜

| 鍵 | 取值 |
|---|---|
| `card.coverDirection` 封面位置 | `top`（上）、`left`（左）、`right`（右） |
| `card.coverDisplayMode` 封面樣式 | `rectangle`（矩形）、`circle`（圓形）、`full`（覆蓋） |
| `sort[].sortType` 排序方向 | `1` 升序、`2` 降序 |
| `config.mode` 詳情檢視 | `all` 常規多條、`first` 只看第一條 |
| `rowHeight` 行高 | `0` 緊湊、`1` 中等、`2` 高、`3` 超高 |

- **`tableFields` 對錶格檢視是真的限制列**：列出哪幾列就只顯示哪幾列，順序也照給的來。其它檢視
  型別上它表示卡片上顯示哪些欄位。
- **`filterList`（左側分類）只能給一個欄位**，給兩個及以上會被拒絕——介面上本來也只能選一個。
- **`quickFilters` 只寫欄位 ID 就行**，每項的型別按欄位自動定，不必自己猜配哪種比較方式。
- **相對時間視窗**：篩選條件裡用 `dateRange` 表示「最近 N 天」這類相對視窗（`0` = 用絕對值），
  粒度用 `dateRangeType`。這兩個鍵**只在日期欄位上有意義**。
- `filter` / `enableWhen` 跟其它篩選是同一種寫法 `{"logic","items":[{"field","op","value"}]}`，見
  `hap guide record filter`。檢視這邊能用的比較方式看 3.2 那張表的「檢視/規則/按鈕/圖表」一列——
  比記錄查詢多出 `self`、`rc_eq`、`array_eq`、`date_is` 這些；日期列上照常寫 `between` / `gt` /
  `lte`，`hap` 會按列型別自動換成日期專用的比較方式。舊的 `{"type":"group","children":[…]}` 那棵樹仍然可用。

#### 外掛檢視與多表層級

```jsonc
{"viewType": "plugin", "plugin": {"id": "<插件ID>", "name": "甘特增强"}}

{"viewType": "hierarchy", "config": {"childType": 2},
 "viewControls": [{"worksheetId": "<表ID>", "worksheetName": "..."}]}
```

`plugin` 只寫一個字串時當作外掛 id。多表層級要 `config.childType: 2`，每層的表寫在
`viewControls` 裡；單表層級（自關聯）仍是 `childType: 1` 加 `config.relationField`。

同一層還可以給 `layersName`、`customDisplay`、`unRead`、`alias`，都按原樣送出。

---

下面 §1–§3 是 **wire 層**：`view update --edit-attrs` / `--edit-ad-keys` 直接寫的鍵。
未覆蓋的鍵以讀命令（`hap --json worksheet view info`）返回的實際結構為準。

### 1. viewType 列舉

| viewType | 名稱 | 含義 |
|---|---|---|
| 0 | sheet | 表格檢視 |
| 1 | board | 看板檢視 |
| 2 | structure | 層級檢視 |
| 3 | gallery | 畫廊檢視 |
| 4 | calendar | 日曆檢視 |
| 5 | gunter | 甘特檢視 |
| 6 | detail | 詳情檢視 |
| 7 | resource | 資源檢視 |
| 8 | map | 地圖檢視 |
| 21 | customize | 外掛檢視 |

`childType` 修飾符：詳情檢視 `1`=單條詳情、`2`=多條列表+詳情；層級檢視 `1`=單表層級（自關聯）、`2`=多表層級。

### 2. editAttrs — 頂層檢視屬性

`view update --edit-attrs` 可寫的頂層屬性。複雜值先讀後改。

| attr | 含義 | 值形態 |
|---|---|---|
| `name` | 檢視名（改名） | string |
| `advancedSetting` | 設定項字串字典；**必須配 `--edit-ad-keys`**（見 §3） | 值全為字串的物件 |
| `AdvancedSetting` | 服務端接受的首字母大寫別名 | 同上 |
| `filters` | 檢視過濾條件 | 讀回是 → [FilterCondition[]](../scripts/types/filter-condition.schema.json)；寫入時 `--filter-json` / `--view-spec` 的 `filter` 用統一寫法 `{logic, items:[{field, op, value}]}` |
| `fastFilters` | 快速篩選欄位配置 | 陣列 `[{controlId, dataType, spliceType, filterType, advancedSetting{…}}]`，每項的 advancedSetting 為模組專屬結構，先讀後改 |
| `moreSort` | 多欄位排序 | → [SortItem[]](../scripts/types/sort-item.schema.json) |
| `sortCid` | 主排序欄位 | controlId 字串 |
| `sortType` | 主排序方向 | int：`1`=升序 `2`=降序 |
| `controls` | 欄位配置中的隱藏欄位列表（個人儲存場景下＝個人隱藏列） | controlId 的陣列 |
| `displayControls` | 卡片 / 移動端列表顯示的欄位 | controlId 的陣列 |
| `showControls` | 表格顯示列（`customdisplay='1'` 時生效） | controlId 的陣列 |
| `ShowControls` | 大寫別名（列隱藏儲存路徑） | 同上 |
| `controlsSorts` | 卡片欄位顯示順序 | controlId 的陣列 |
| `customDisplay` | 移動端使用獨立顯示欄位列表 | boolean |
| `coverCid` | 封面圖片欄位 | controlId 字串 |
| `coverType` | 封面填充方式 | int：`0`=填滿 `1`=完整顯示 |
| `showControlName` | 卡片上顯示欄位名 | boolean |
| `rowHeight` | 行高 | int：表格 `0`緊湊/`1`中等/`2`高/`3`超高；資源 `0`緊湊/`1`寬鬆 |
| `viewControl` | 分組/維度欄位（看板分組、層級父欄位、日曆/地圖/資源主欄位） | controlId 字串 |
| `viewControls` | 多表層級的層定義 | 陣列 `[{worksheetId, controlId, …}]`，先讀後改 |
| `layersName` | 多表層級各層顯示名 | string 的陣列 |
| `childType` | 見 §1 | int `1`\|`2` |
| `navGroup` | 篩選列表分組欄位 | 最多 1 項的陣列 `[{controlId, viewId?, filterType?, isAsc?}]` |
| `personal_setting` | 標誌屬性：與 `controls` 同傳時把改動存入**個人層**而非共享檢視；資料落在 `advancedSetting.personal_setting` | JSON 字串 `{"controls":[…],"controlsSorts":[…]}` |
| `pluginId` | 外掛檢視繫結的外掛 id | string |

> 讀返回裡還會出現 `pluginName` / `pluginIcon` / `pluginIconColor` / `pluginSource`
> 等外掛元資料鍵，按讀到的實際結構處理。

### 3. editAdKeys — advancedSetting 子鍵

`--edit-ad-keys` 可指定的子鍵。**所有值都是字串**；JSON 結構需序列化為字串。

#### 3.1 表格（sheet）

| 鍵 | 含義 | 值形態 | 適用 |
|---|---|---|---|
| `sheettype` | 表格互動風格 | `"0"`=經典 `"1"`=電子表格 | 表格 |
| `fastedit` | 行內直接編輯 | `"1"`=開（預設） `"0"`=關 | 表格 |
| `enablerules` | 檢視內啟用業務規則 | `"1"`=開（預設） `"0"`=關 | 表格 |
| `rctitlestyle` | 記錄標題樣式 | 列舉字串，`"0"`=預設 | 表格 |
| `showno` | 顯示行號 | `"1"`=開（預設） `"0"`=關 | 表格 |
| `showquick` | 顯示記錄快捷選單（…） | `"1"`=開（預設） `"0"`=關 | 表格 |
| `showsummary` | 顯示彙總行 | `"1"`=開（預設） `"0"`=關 | 表格 |
| `showvertical` | 顯示縱向網格線 | `"1"`=開（預設） `"0"`=關 | 表格 |
| `alternatecolor` | 隔行換色 | `"1"`=開 `"0"`=關（預設關） | 表格 |
| `titlewrap` | 表頭換行 | `"1"`=開 `"0"`=關（預設關） | 表格 |
| `liststyle` | 各列寬度/樣式 | JSON 字串 `{"time":<毫秒>,"styles":[{cid, width?, …}]}` | 表格 |
| `fixedcolumncount` | 凍結列數 | 數字字串 | 表格 |
| `layoutupdatetime` | 佈局最後儲存時間戳 | epoch 毫秒字串 | 表格 |
| `customdisplay` | `"1"`=檢視用自己的列表（`showControls`）`"0"`=跟隨表單佈局 | `"0"`\|`"1"` | 表格 |
| `customShowControls` | `customdisplay='0'` 時暫存的自訂列清單 | controlId 的 JSON 陣列（字串） | 表格 |
| `sysids` | 跟隨表單佈局時可見的系統欄位 | controlId 的 JSON 陣列（字串） | 表格 |
| `syssort` | 系統欄位順序 | controlId 的 JSON 陣列（字串） | 表格 |
| `personal_setting` | 使用者個人的列隱藏/排序 | JSON 字串 `{"controls":[ids],"controlsSorts":[ids]}` | 表格 |

#### 3.2 排序 / 過濾 / 重新整理 / 連結引數（各類檢視通用）

| 鍵 | 含義 | 值形態 | 適用 |
|---|---|---|---|
| `closedefsort` | 清空自訂排序後禁用預設排序 | `"0"`\|`"1"` | 全部 |
| `refreshtime` | 自動重新整理間隔（秒），`"0"`=關 | 列舉字串：`"0"`,`"30"`,`"60"`,… | 全部 |
| `urlparams` | 檢視過濾可引用的 URL 引數 | 引數名字串的 JSON 陣列（每個 ≤20 字元） | 全部 |
| `clicksearch` | 快篩：`"1"`=執行查詢後才顯示資料 | `"0"`\|`"1"` | 配了快篩的檢視 |
| `enablebtn` | 快篩：顯示「查詢」按鈕（>3 個篩選時強制開） | `"0"`\|`"1"` | 配了快篩的檢視 |
| `fastrequired` | 快篩：查詢前必填開關 | `"0"`\|`"1"`\|`""` | 配了快篩的檢視 |
| `requiredcids` | 快篩：必填的篩選欄位 id | controlId 的 JSON 陣列（字串） | 配了快篩的檢視 |
| `showhide` | 檢視在導航中的可見性 | `"show"`=顯示 `"hide"`=隱藏 `"hpc&sapp"`=僅 PC 隱藏 `"spc&happ"`=僅移動端隱藏 | 全部 |

#### 3.3 記錄點選與自訂按鈕（表格 + 卡片類）

| 鍵 | 含義 | 值形態 | 適用 |
|---|---|---|---|
| `clicktype` | 點記錄的動作 | `"0"`=開啟記錄 `"1"`=開啟連結 `"2"`=無 | 表格/卡片類 |
| `clickcid` | `clicktype='1'` 時使用的連結欄位 | controlId 字串 | 同上 |
| `listbtns` | 列表/行區顯示的自訂按鈕 | 按鈕 id 的 JSON 陣列（字串） | 表格/卡片類 |
| `detailbtns` | 記錄詳情中按鈕的順序 | 按鈕 id 的 JSON 陣列（字串） | 全部 |
| `hidebtn` | 隱藏不可用按鈕 | `""`\|`"1"` | 全部 |
| `acstyle` | 按鈕樣式配置 | JSON 物件字串，先讀後改 | 全部 |
| `actioncolumn` | 行「操作列」配置（按鈕、寬度等） | JSON 物件字串，先讀後改 | 表格、層級（表格模式） |

#### 3.4 卡片外觀（看板/畫廊/層級/日曆/甘特/詳情/地圖/資源 的卡片）

| 鍵 | 含義 | 值形態 | 適用 |
|---|---|---|---|
| `viewtitle` | 卡片/記錄標題欄位 | controlId 字串 | 卡片類、甘特標籤 |
| `abstract` | 卡片摘要欄位 | controlId 字串，`""`=無 | 卡片類 |
| `maxlinenum` | 摘要最多顯示行數（1–5） | 數字字串 | 卡片類 |
| `cardwidth` | 卡片寬度 | `"1"`=小 `"2"`=中 `"3"`=大 `"4"`=超大 `"5"`=自訂 | 看板/畫廊/層級 |
| `coverposition` | 封面位置 | `"2"`=上 `"1"`=左 `"0"`=右 | 卡片類 |
| `coverstyle` | 封面顯示模式 | `"0"`=覆蓋 `"2"`=圓形 `"3"`=矩形 | 卡片類 |
| `opencover` | 點選封面可預覽 | `"1"`=允許（預設） `"2"`=不允許 | 卡片類 |
| `showcount` | 卡片預設顯示欄位數；不設=關 | 數字字串 | 卡片類 |
| `emptyname` | 「未指定」看板的自訂名稱 | string | 看板 |
| `navempty` | 啟用「未指定」看板 | `"1"`=開 `"0"`=關 | 看板 |
| `freezenav` | 滾動時凍結第一個看板 | `"0"`\|`"1"` | 看板 |

#### 3.5 分組與篩選列表導航

`navshow`/`navfilters` 由看板分組、畫廊分組、篩選列表、資源檢視共用。

| 鍵 | 含義 | 值形態 | 適用 |
|---|---|---|---|
| `navshow` | 顯示哪些分組項 | `"0"`=全部 `"1"`=有資料的項 `"2"`=指定項 `"3"`=滿足篩選條件的項 | 看板/畫廊分組、篩選列表、資源 |
| `navfilters` | `navshow='2'`：指定項 id/值的 JSON 陣列；`navshow='3'`：→ [FilterCondition[]](../scripts/types/filter-condition.schema.json)（序列化為字串） | JSON 字串，形態隨 navshow 變化，先讀後改 | 同上 |
| `navsorts` | 分組項自訂順序 | JSON 陣列（字串） | 看板/篩選列表 |
| `customitems` | 自訂/合併的分組項 | JSON 陣列字串，先讀後改 | 看板/畫廊分組 |
| `customnavs` | 篩選列表自訂導航項 | JSON 陣列字串，先讀後改 | 篩選列表 |
| `navlayer` | 層級型分組欄位顯示的層數，`"999"`=全部 | 數字字串 | 篩選列表 |
| `navwidth` | 篩選列表面板預設寬度 px（100–500） | 數字字串 | 篩選列表 |
| `usenav` | 新建記錄時把選中項作為預設值 | `"0"`\|`"1"` | 篩選列表 |
| `navsearchtype` | 導航搜尋模式 | `"0"`=模糊 `"1"`=精確 | 篩選列表 |
| `navsearchcontrol` | 導航內搜尋的欄位（關聯記錄分組） | controlId 字串 | 篩選列表 |
| `showallitem` | 「全部」項 | `""`=顯示 `"1"`=隱藏 | 篩選列表/看板分組 |
| `allitemname` | 「全部」項的自訂名稱 | string | 篩選列表/看板分組 |
| `shownullitem` | 顯示「為空」項 | `"1"`=顯示 | 篩選列表/看板分組 |
| `nullitemname` | 「為空」項的自訂名稱 | string | 篩選列表/看板分組 |
| `appnavtype` | 移動端導航展示型別（關聯/級聯欄位固定 `"2"`） | `"1"`\|`"2"`\|`"3"` | 篩選列表（移動端） |
| `showNextGroup` | 自動展開下一層分組（與 navshow `"2"` 搭配，`"999"`） | 數字字串 | 篩選列表 |
| `groupsetting` | 表內分組欄位配置 | JSON 陣列字串 `[{controlId,…}]`，先讀後改 | 表格（分組）、看板 |
| `groupshow` | 表內分組版 `navshow` | 同 navshow 取值 | 表格分組 |
| `groupfilters` | 表內分組版 `navfilters` | 同 navfilters，先讀後改 | 表格分組 |
| `groupsorts` | 表內分組版 `navsorts` | JSON 陣列（字串） | 表格分組 |
| `groupcustom` | 表內分組版 `customitems` | JSON 陣列字串，先讀後改 | 表格分組 |
| `groupempty` | 顯示「未分組」組 | `""`\|`"1"` | 表格分組 |
| `groupemptyname` | 「未分組」自訂名稱 | string | 表格分組 |
| `groupopen` | 分組預設狀態 | `"1"`=展開第一個 `"2"`=展開全部 `"3"`=收起全部 | 表格分組 |

#### 3.6 層級（structure）

| 鍵 | 含義 | 值形態 | 適用 |
|---|---|---|---|
| `hierarchyViewType` | 展示模式 | `"0"`=橫向 `"1"`=豎向 `"2"`=混合 `"3"`=樹形表格 | 層級 |
| `hierarchyViewConnectLine` | 連線線樣式 | 列舉字串 | 層級 |
| `minHierarchyLevel` | 混合模式豎向層數 | 數字字串 | 層級 |
| `topshow` | 頂層範圍 | `"0"`=全部頂層 `"3"`=滿足條件的項 `"2"`=指定項 | 層級 |
| `topfilters` | `topshow='3'`：→ [FilterCondition[]](../scripts/types/filter-condition.schema.json)（序列化為字串）；`topshow='2'`：id 的 JSON 陣列 | JSON 字串，先讀後改 | 層級 |
| `defaultlayer` | 預設展開層數 | `"1"`–`"5"` | 層級 |
| `defaultlayertime` | defaultlayer 修改時間戳 | epoch 毫秒字串 | 層級 |
| `treestyle` | 樹形表格樣式 | 列舉字串，預設 `"1"` | 層級（表格模式） |

#### 3.7 日曆 / 甘特 / 資源（時間類）

| 鍵 | 含義 | 值形態 | 適用 |
|---|---|---|---|
| `begindate` | 開始日期/時間欄位 | controlId 字串 | 日曆/甘特/資源 |
| `enddate` | 結束日期/時間欄位 | controlId 字串 | 日曆/甘特/資源 |
| `calendarcids` | 多組起止時間對（多事件） | JSON 字串 `[{"begin":"<cid>","end":"<cid>"}]` | 日曆 |
| `calendarType` | 預設刻度 | `"0"`=月 `"1"`=周 `"2"`=日（資源檢視取值更多） | 日曆、資源 |
| `calendartype` | 甘特預設刻度（注意全小寫 t） | 列舉字串 | 甘特 |
| `weekbegin` | 每週起始日 | `"1"`–`"7"` | 日曆/資源 |
| `unweekday` | 隱藏的星期位，如 `"67"`=隱藏週六日；`""`=全顯示 | 數字位字串 | 日曆/甘特/資源 |
| `unlunar` | 農曆顯示 | `"0"`=顯示 `"1"`=隱藏 | 日曆 |
| `hour24` | 24 小時制 | `"0"`\|`"1"` | 日曆/資源 |
| `showall` | 顯示全部事件/寬鬆行 | `"0"`\|`"1"` | 日曆 |
| `showtime` | 工作時段，如 `"08:00-18:00"`；不設=全天 | `HH:mm-HH:mm` 字串 | 日曆/資源 |
| `rowHeight` | 日曆行密度（advancedSetting 內變體；資源檢視用頂層屬性） | `"0"`=緊湊 `"1"`=寬鬆 | 日曆 |
| `milepost` | 里程碑欄位（檢查項型別） | controlId 字串 | 甘特 |
| `navtitle` | 左側導航記錄標籤欄位 | controlId 字串 | 甘特 |
| `showgroupcolor` | 顯示分組顏色 | `"0"`\|`"1"` | 甘特 |

#### 3.8 詳情檢視

| 鍵 | 含義 | 值形態 | 適用 |
|---|---|---|---|
| `showtitle` | 顯示記錄標題（地圖檢視複用為地點標籤） | `""`=顯示（預設） `"0"`=隱藏 | 詳情、地圖 |
| `showtoolbar` | 顯示操作工具欄 | `""`=顯示 `"0"`=隱藏 | 詳情 |

#### 3.9 地圖檢視

| 鍵 | 含義 | 值形態 | 適用 |
|---|---|---|---|
| `maplocation` | 預設地圖中心/縮放配置 | JSON 物件字串（center、zoom…），先讀後改 | 地圖 |
| `tagType` | 地點標記展示型別 | 列舉字串 | 地圖 |
| `tagcolorid` | 給標記上色的選項欄位 | controlId 字串 | 地圖 |

#### 3.10 記錄顏色

| 鍵 | 含義 | 值形態 | 適用 |
|---|---|---|---|
| `colorid` | 提供記錄顏色的單選/多選欄位 | controlId 字串 | 表格/看板/畫廊/層級/日曆/甘特 |
| `colortype` | 顏色展示方式，`"0"`=預設 | 列舉字串 | 同上 |
| `coloritems` | 顯示哪些顏色項：`""`=全部，否則指定項 | `""` 或 JSON 陣列（字串） | 同上 |

#### 3.11 移動端顯示

| 鍵 | 含義 | 值形態 | 適用 |
|---|---|---|---|
| `appshowtype` | 移動端卡片佈局型別（預設 `"0"`＝一行三列、限 3 欄位） | 列舉字串 | 表格/卡片類（移動端） |
| `checkradioid` | 移動端卡片上顯示的檢查項欄位 | controlId 字串 | 移動端 |
| `rowcolumns` | 移動端每行欄位數 | `"1"`\|`"2"` | 移動端 |

#### 3.12 外掛檢視（customize）

| 鍵 | 含義 | 值形態 | 適用 |
|---|---|---|---|
| `environmentparams` | 傳給外掛的環境引數 | JSON 物件字串（自由鍵值） | 外掛 |
| `plugin_map` | 按欄位 id 存放的外掛引數值 | JSON 物件字串 `{"<fieldId>": value}` | 外掛 |
| `plugin_attachement_info` | 鎖定的外掛版本資訊 | JSON 物件字串，先讀後改 | 外掛 |

> 注意兩類同名不同層的鍵：快篩**每個篩選項內部**的 advancedSetting（`allowscan`、
> `daterange`、`allowitem`、`direction`、`searchtype`、`searchcontrol`、`limit`、
> `defsource`、`showtype` 等）住在 `fastFilters[].advancedSetting` 裡，不是檢視級
> editAdKeys；`shownullitem`/`nullitemname` 在檢視級（§3.5）和單個快篩項裡**都**存在，
> 改之前用 `view info` 確認你要動的是哪一層。
