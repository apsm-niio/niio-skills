# 工作表與欄位 — 命令參考與資料字典

> **全域性規則：改複雜值前先用讀命令匯出現狀，在真實結構上改，再寫回。**

## 呼叫正規化

### 工作表

```bash
# 新建（可一并铺好字段；--fields 即下文 FieldSpec 高层方言）
hap worksheet create 1f2e3d4c-5b6a-7081-92a3-b4c5d6e7f809 "客户" \
  --icon table --remark "客户主数据" \
  --fields '[{"type":"TEXT","name":"客户名称","required":true},
             {"type":"MOBILE_PHONE","name":"电话"},
             {"type":"DROP_DOWN","name":"等级","options":["VIP","普通"]}]' \
  --title-name 客户名称

# 基本信息；表单布局与视图列表可以顺带取回，不必再发两条命令
hap --json worksheet info 6845f0a1b2c3d4e5f6a7b8c9
hap --json worksheet info 6845f0a1b2c3d4e5f6a7b8c9 --with-form --with-views

# 改别名 / 描述；改侧边栏名称、图标或显示状态需要 --app-id
hap worksheet update 6845f0a1b2c3d4e5f6a7b8c9 --alias customers --desc "客户主数据"
hap worksheet update 6845f0a1b2c3d4e5f6a7b8c9 --name "客户（CRM）" \
  --app-id 1f2e3d4c-5b6a-7081-92a3-b4c5d6e7f809

# 从应用导航里隐藏（表本身照常可用、数据照常读写）
hap worksheet update 6845f0a1b2c3d4e5f6a7b8c9 --visibility hidden \
  --app-id 1f2e3d4c-5b6a-7081-92a3-b4c5d6e7f809

# 删除
hap worksheet delete 6845f0a1b2c3d4e5f6a7b8c9 --app-id 1f2e3d4c-5b6a-7081-92a3-b4c5d6e7f809 -y

# 字段清单。默认输出是高层归一形态；--raw 输出服务端原始控件（WireControl），
# 任何「读改写」操作都以 --raw 为准
hap --json worksheet fields 6845f0a1b2c3d4e5f6a7b8c9
hap --json worksheet fields 6845f0a1b2c3d4e5f6a7b8c9 --raw
```

`--visibility` 取 `visible` / `hidden` / `pc-hidden` / `mobile-hidden`。**專門用來存另一張表
子記錄的那種表，通常就該設成 `hidden`**——隱藏隻影響導航，不影響讀寫。

### 只存子錶行的工作表：讀它要指出父表

```bash
hap --json worksheet fields <子表工作表ID> --parent <父表工作表ID>
```

這類表**不能單獨讀**，不帶 `--parent` 會直接報讀不了。把現成的表掛成某張表的子表用
`hap worksheet mount-subtable`。

### 🚨 複製工作表：沒點名的關聯列會變成純文字

```bash
hap worksheet copy <工作表ID> "客户-副本" -a <应用ID> \
  --keep-relation <关联字段ID> --keep-relation <子表字段ID>
```

`--keep-relation` 要**逐個點名**（可重複）。**沒被點到的關聯記錄、子表、級聯選擇列，
在副本里會被複製成普通文字列**——資料還在，關係沒了，且沒有任何提示。複製前先
`worksheet fields` 把這些列的 id 列出來。

副本里的列 id 和源表一模一樣是正常的：列 id 只在自己表內唯一，看到兩張表出現相同
controlId 不必去「修」。

### 欄位：先分清「新增」還是「改已有」

欄位寫入有兩條路，**選錯會丟欄位**（尤其是雙向關聯自動生成的反向控制元件）：

| 想做什麼 | 用什麼 |
|---|---|
| **新增**欄位 | `hap worksheet add-fields`（增量、安全），或 edit-spec `field.add` |
| **修改 / 刪除 / 重排**已有欄位 | **edit-spec** `field.update` / `field.delete` / `field.reorder`（`hap app-editor`，自動整表讀改寫） |
| 位元組級控制整張表佈局 | `hap worksheet update-fields --controls`（整表替換，先 `fields --raw` 讀全量） |

#### 新增欄位（增量，安全）

```bash
# 只追加传入的控件，已有列（含反向关联控件）一概不动
hap worksheet add-fields 6845f0a1b2c3d4e5f6a7b8c9 --controls '[
  {"type": 2,  "controlName": "备注"},
  {"type": 15, "controlName": "签约日期"}
]'

# 布局太长放不进命令行时从文件读（--controls / --fields 都支持 @文件名）
hap worksheet add-fields 6845f0a1b2c3d4e5f6a7b8c9 --controls @new-controls.json
```

`--controls` 接 WireControl 原始形態（與 `fields --raw` 輸出同構，見資料字典 §2）。

子表既可以這樣手寫裸控制元件，也可以走 edit-spec 的 `field.add` + `subtable` 塊（新建子表寫它的列，
或把已有表掛上來），後者會連子表側的反向關聯一起配好——見
[edit-spec.md](edit-spec.md) 的「子表有兩種模式」。

> 🚨 **不要自己造 `controlId`。** 省略它，列 id 由服務端鑄。自己填一個（從別處抄來的、
> 或隨手生成的 UUID）會被原樣存下，**那樣的列在表格和關聯控制元件裡讀不出來，永遠是空白**。

嵌入頁、自訂控制元件、查詢記錄、查詢按鈕、API 查詢、OCR、自由連線、分段這幾種以前沒有
模板的型別，現在也能像別的型別一樣按型別名直接建，不必再手寫原始控制元件字典。全部型別名
見 `hap worksheet field-types`。

#### 修改 / 刪除 / 重排：優先走 edit-spec

這三類操作的正確語義是「讀出**全部**原始控制元件 → 只改目標 → 整表寫回」。
`hap app-editor` 的 field op 替你做這個流程，反向/系統控制元件原樣保留：

```json
{
  "app": "1f2e3d4c-5b6a-7081-92a3-b4c5d6e7f809",
  "ops": [
    { "type": "field.add",     "worksheet": "客户",
      "field": { "name": "来源", "type": "SingleSelect", "options": ["展会", "转介绍"] } },
    { "type": "field.update",  "worksheet": "客户",
      "field": "电话", "rename": "联系电话", "set": { "required": true } },
    { "type": "field.delete",  "worksheet": "客户", "field": "旧编号", "confirm": true },
    { "type": "field.reorder", "worksheet": "客户",
      "order": ["客户名称", "联系电话", "等级", "来源"] }
  ]
}
```

```bash
hap app-editor validate edit.json   # 本地校验，零网络
hap app-editor plan     edit.json   # dry-run：读实时结构，预演每个 op
hap app-editor apply    edit.json   # 逐 op 执行（--continue 失败不中断）
```

要點：

- `field.add` 走增量追加；`field` 裡 `type` 接 CODE（Text/Number/Relation…）、
  型別名（TEXT/RELATE_SHEET…）或整數。欄位詞彙是
  `name` / `type` / `required` / `unique` / `options` / `relation` / `lookup` / `rollup` /
  `formula` / `subtable` / `control`——跨表型別必須帶自己那個塊，寫法見
  [edit-spec.md](edit-spec.md) 的「field 的跨表塊」。詞表以外的鍵、塊放錯型別、塊內未知鍵
  一律**校驗報錯**，不會靜默建出指向為空的壞列。這份詞彙沒建模的形狀走
  `control:{<WireControl 原始键>}` 逃生口（最後合併、優先生效）。
- `field.update` 的 `set` 直接寫 WireControl 原始鍵（見 §2/§3）。
- `field.reorder` 按 `order` 重排顯示順序（順序由控制元件 `row` 決定）；未列出的欄位接在後面。
- 元素可用名稱或 id 引用，spec 內後面的 op 可引用前面剛建的元素。

#### 整表替換（update-fields）：知道自己在做什麼再用

`update-fields` 把傳入內容當作**完整佈局**：沒傳的列一律刪除，包括系統自動生成的
反向關聯控制元件。僅兩種場景使用：

```bash
# 保存前先干跑检查（一个字都不写），保存后默认自动回读比对
hap worksheet update-fields 6845f0a1b2c3d4e5f6a7b8c9 --fields @layout.json --check
hap worksheet update-fields 6845f0a1b2c3d4e5f6a7b8c9 --fields @layout.json
hap worksheet update-fields 6845f0a1b2c3d4e5f6a7b8c9 --fields @layout.json --no-verify

# 场景 A：刚建的空表一次铺设全部字段（高层方言 --fields）
hap worksheet update-fields 6845f0a1b2c3d4e5f6a7b8c9 --title-name 客户名称 --fields '[
  {"type":"TEXT", "name":"客户名称", "required":true},
  {"type":"AUTO_ID", "name":"客户编号",
   "advanced_setting":{"increase":
     "[{\"type\":1,\"repeatType\":0,\"start\":1,\"length\":5,\"format\":\"C-\"}]"}},
  {"type":"DROP_DOWN", "name":"等级", "options":["VIP","普通","潜在"]}
]'

# 场景 B：完整读出 → 在真实结构上改 → 整表写回（--raw + --controls，这条路干净往返）
hap --json worksheet fields 6845f0a1b2c3d4e5f6a7b8c9 --raw > controls.json
# ……编辑 controls.json：只动目标控件，其余键原样保留……
hap worksheet update-fields 6845f0a1b2c3d4e5f6a7b8c9 --controls @controls.json --check
hap worksheet update-fields 6845f0a1b2c3d4e5f6a7b8c9 --controls @controls.json
```

坑位提示：

- **永遠不要**用 update-fields 來「加一個欄位」——加欄位用 add-fields 或 `field.add`。
- 新建工作表自帶的 名稱/描述/附件 列在 update-fields 後會被丟棄，想保留就顯式傳回。
- 寫回時未知鍵原樣保留，不要清洗你看不懂的鍵。
- **條目帶不帶 `id` 決定它是改已有列還是建新列**：帶 `id`（`worksheet fields` 輸出裡的那個）
  就是改那一列，資料留著；不帶 `id` 當成新列由服務端鑄 id，而原來那一列如果沒出現在這次
  列表裡，它和它存的資料一起消失。
- **儲存成功 ≠ 儲存對了**：引用了已不存在的欄位、表單裡留下空行、同一列出現兩次，這些都能
  儲存成功而不報錯。`--check` 只報告問題不寫入，改結構前先跑一次；真正儲存後會**自動回讀**
  把這次留下的問題報出來（要關掉用 `--no-verify`）。看到報告別當噪音。
- `--fields` 和 `--controls` 都接受 **`@文件名`**：真實整表佈局遠超一條命令列能承載的長度。

### 雙向關聯：一對列，不是一個開關

關聯欄位預設單向：A 表能點名 B 表的記錄，B 表看不到 A。要雙向，在欄位 `config` 裡開
`bidirectional` 並給對方表上那一列起名，**一次建好兩側**：

```bash
hap worksheet add-fields <订单表ID> --controls '[
  {"type": 29, "controlName": "客户", "dataSource": "<客户表工作表ID>",
   "advancedSetting": {"bidirectional": "1", "showtype": "1"}}
]'
```

或走整表佈局的高層方言（`update-fields --fields` / `worksheet create --fields`）：

```json
{"type":"RELATE_SHEET", "name":"客户", "dataSource":"<客户表工作表ID>",
 "config":{"bidirectional": true, "reverseName": "订单", "displayMode": "card"}}
```

走 edit-spec 時用 `relation` 塊，目標表和展示列都可以寫名字：

```json
{ "type": "field.add", "worksheet": "订单",
  "field": { "name": "客户", "type": "RELATE_SHEET",
             "relation": { "worksheet": "客户", "multiple": false,
                           "showFields": ["客户名称", "等级"] } } }
```

> `relation` 塊本身**不含 `bidirectional`**（塊內未知鍵會被校驗拒絕）。edit-spec 裡要雙向，
> 先用 `relation` 塊把關聯建出來，再 `hap worksheet pair-relation` 補反向端；或者把
> `advancedSetting` 塞進 `control` 逃生口。詞彙與校驗規則見
> [edit-spec.md](edit-spec.md) 的「field 的跨表塊」。

- 這會在客戶表上**真的建出一列**「訂單」。`reverseName` 是對方表上那列的名字，不給就用本表名。
- `displayMode` 取 `dropdown` / `card` / `inlineTable` / `tabTable`。
- 已經有好幾條反向關聯的表，改結構時**用 `add-fields` 或 `field.add` 加列**，別整體替換佈局——
  反向列很容易在替換裡被漏掉。

#### 給已存在的關聯欄位補反向端

建的時候沒開 `bidirectional`，事後要補，用 `pair-relation`，**不要去改佈局**：

```bash
hap worksheet pair-relation <工作表ID> 客户                # FIELD 传列名或字段 ID
hap worksheet pair-relation <工作表ID> 客户 --name 订单     # 指定对方表上那列的名字
hap worksheet pair-relation <工作表ID> 客户 --repair       # 覆盖对方表上的残留列
```

> 🚨 **不要用「佔位 `sourceControlId`」自己偽造反向端。** 那樣建出來的關聯服務端並沒有登記成
> 反向端，而且**之後每做一次整表替換，這個欄位就會被複制多出一份**，越改越多。已經這麼配過的
> 表用 `--repair` 收拾：它覆蓋對方表上的殘留列（含重複的多份），**只重寫那一列，兩張表其餘列不動**。
> 不加 `--repair` 時命令會先停下來告訴你有殘留，不會擅自覆蓋。

#### 怎麼判斷一個關聯到底是不是雙向

看 `hap worksheet fields` 輸出裡該欄位的 `relation.bidirectional`：`true`/`false` 是已查證的
結論，**`null` 表示查不出來**（通常是對方表沒有讀取許可權）。

**不能用「有沒有 `sourceControlId`」判斷雙向**——單向關聯也帶著它，那只是給反向端預留的位置，
目標表裡並不存在這麼一列。只有去對方表裡找得到那一列才算數。

## 資料字典

字典核對於 hap-cli 0.9.0；未覆蓋的鍵以讀命令（`hap --json worksheet fields <id> --raw`）返回的實際結構為準。
速查用 `hap worksheet field-types`（它是執行時生成的，與本表不一致時以它為準）。

### 1. 控制元件型別列舉（`type` 整數）

`--fields` / edit-spec 的 `type` 接受三種寫法：整數、型別名（TEXT…）、CODE（Text…）。

| type | 型別名 | CODE | 含義 |
|---|---|---|---|
| 2 | TEXT | Text | 文字（`enumDefault` 1=多行 2=單行） |
| 3 | MOBILE_PHONE | PhoneNumber | 手機號 |
| 4 | TELEPHONE | LandlinePhone | 座機 |
| 5 | EMAIL | Email | 郵箱 |
| 6 | NUMBER | Number | 數值 |
| 7 | CRED | Certificate | 證件 |
| 8 | MONEY | Currency | 金額 |
| 9 | FLAT_MENU | SingleSelect | 單選（平鋪） |
| 10 | MULTI_SELECT | MultipleSelect | 多選 |
| 11 | DROP_DOWN | Dropdown | 單選（下拉） |
| 14 | ATTACHMENT | Attachment | 附件 |
| 15 | DATE | Date | 日期 |
| 16 | DATE_TIME | DateTime | 日期+時間 |
| 19 | AREA_PROVINCE | Region(province) | 地區（省） |
| 21 | RELATION | DynamicLink | 自由連線（舊式） |
| 22 | SPLIT_LINE | Divider | 分段 |
| 23 | AREA_CITY | Region(city) | 地區（省-市） |
| 24 | AREA_COUNTY | Region(county) | 地區（省-市-縣） |
| 25 | MONEY_CN | AmountInWords | 大寫金額 |
| 26 | USER_PICKER | Collaborator | 成員 |
| 27 | DEPARTMENT | Department | 部門 |
| 28 | SCORE | Rating | 等級/評分 |
| 29 | RELATE_SHEET | Relation | 關聯記錄 |
| 30 | SHEET_FIELD | Lookup | 他表欄位 |
| 31 | FORMULA_NUMBER | Formula | 數值公式 |
| 32 | CONCATENATE | Concatenate | 文字組合 |
| 33 | AUTO_ID | AutoNumber | 自動編號 |
| 34 | SUB_LIST | SubTable | 子表 |
| 35 | CASCADER | CascadingSelect | 級聯選擇 |
| 36 | SWITCH | Checkbox | 檢查框/開關 |
| 37 | SUBTOTAL | Rollup | 彙總 |
| 38 | FORMULA_DATE | DateFormula | 日期公式 |
| 39 | — | CodeScan | 掃碼 |
| 40 | LOCATION | Location | 定位 |
| 41 | RICH_TEXT | RichText | 富文字 |
| 42 | SIGNATURE | Signature | 簽名 |
| 43 | OCR | OCR | 文字識別 |
| 44 | — | Role | 角色 |
| 45 | EMBED | Embed | 嵌入 |
| 46 | TIME | Time | 時間 |
| 47 | BAR_CODE | Barcode | 條碼 |
| 48 | ORG_ROLE | OrgRole | 組織角色 |
| 49 | SEARCH_BTN | Button | API 查詢按鈕 |
| 50 | SEARCH | APIQuery | API 查詢 |
| 51 | RELATION_SEARCH | QueryRecord | 查詢記錄 |
| 52 | SECTION | Section | 標籤頁（注意：不是 22 分段） |
| 53 | FORMULA_FUNC | FunctionFormula | 函式公式 |
| 54 | CUSTOM | CustomField | 自訂（外掛）元件 |
| 10010 | REMARK | Remark | 備註（靜態文字） |

地區類的 CODE 統一是 `Region`，由 `regionLevel`（`"province"`/`"city"`/`"county"`，
預設 county）分流到 19/23/24。

### 2. WireControl 常用頂層鍵

服務端原始控制元件物件，完整定義 → [WireControl](../scripts/types/wire-control.schema.json)。
服務端接受部分欄位，按型別補預設值；活控制元件攜帶的鍵比下表多，**寫回時未知鍵原樣保留**。

| 鍵 | 含義 | 值形態 |
|---|---|---|
| `controlId` | 欄位 id；**新建時必須省略**（服務端鑄；自造的 id 會建出永遠讀不出值的空白列），更新時必傳 | string |
| `controlName` | 欄位顯示名 | string |
| `type` | 控制元件型別（見 §1） | int 列舉 |
| `alias` | API 別名（記錄讀寫時可用） | string |
| `required` | 表單必填 | bool |
| `unique` | 禁止重複值 | bool |
| `attribute` | `1`=本表標題欄位（每表恰一個） | int `0`\|`1` |
| `row` / `col` | 0 起的網格位置；row 順序＝顯示順序；col 為行內列（0/1） | int |
| `size` | 12 柵格跨度 | int：`3`\|`6`（半行）\|`12`（整行） |
| `hint` | 輸入佔位提示 | string |
| `options` | 選項列表（type 9/10/11） | 陣列 `[{key(uuid), value, isDeleted, index, checked, color}]` |
| `advancedSetting` | 按型別的設定袋；**值全是字串**，JSON 結構序列化後放入 | 字串值的物件（見 §3） |
| `dataSource` | 型別專屬橋接：RELATE_SHEET/SUB_LIST(掛載)=目標 worksheetId；SUB_LIST(內聯)=新 UUID；SHEET_FIELD/SUBTOTAL=`$<桥接controlId>$`；公式類=表示式字串 `$id$ * $id$` | string |
| `sourceControlId` | SHEET_FIELD：目標表被對映列 id；SUBTOTAL：被聚合列 id | controlId 字串 |
| `enumDefault` | 按型別的判別值：TEXT `1`=多行 `2`=單行；RELATE_SHEET `1`=單條 `2`=多條；ATTACHMENT `3`；SCORE `1`；SUBTOTAL=聚合方式 | int（按型別） |
| `enumDefault2` | 次級判別值（如 MONEY=2、AREA_COUNTY=3） | int（按型別） |
| `strDefault` | 按型別的位標誌串（如 RELATE_SHEET `"000"`、SHEET_FIELD `"10"`），語義不全明，先讀後改 | 數字位字串 |
| `showControls` | RELATE_SHEET / SUB_LIST：在選擇器/內聯列表中展示的關聯欄位 | controlId 的 JSON 陣列 |
| `relationControls` | SUB_LIST：完整子控制元件物件列表（內聯新建或掛載已有表） | 控制元件物件陣列，先讀後改 |
| `userPermission` | 成員/部門欄位許可權標誌（預設 1） | int |
| `fieldPermission` | 三位串：能否看見 / 能否編輯 / 新建記錄時能否看見。與角色許可權**按位與**之後才是最終結果 | `"111"` 這樣的三位串 |
| `controlPermissions` | 同上三位，欄位自身允許的部分；`fields` 輸出的 `isHidden` / `isReadOnly` / `isHiddenOnCreate` 就是這兩串按位與算出來的 | 三位串 |
| `dot` | 小數位（NUMBER 預設 0、MONEY/FORMULA_NUMBER 預設 2） | int |

### 3. 各控制元件型別高價值 advancedSetting 鍵

值全為字串（布林寫 `"1"`/`"0"`）。

| 型別 | 鍵 | 含義 | 值形態 |
|---|---|---|---|
| NUMBER (6) | `showtype` | 顯示：`"0"`=數值 `"1"`=進度 `"2"`=滑塊 | 列舉字串 |
| NUMBER (6) | `roundtype` | 取整方式（`"2"`=四捨五入） | 列舉字串 |
| NUMBER (6) | `thousandth` | 千分位分隔 | `"0"`\|`"1"` |
| NUMBER/SCORE | `itemnames` | 數值區間命名 | JSON 字串 `[{key,value,color}]` |
| MONEY (8) | `currency` | 幣種 | JSON 字串 `{"currencycode":"CNY","symbol":"¥"}` |
| MONEY (8) | `showformat` | 金額顯示格式 | 列舉字串 |
| 選項 9/10/11 | `showtype` | 單選顯示：`"0"`=下拉(→type 11) `"1"`=平鋪(→type 9) `"2"`=進度；切換會連帶改寫 `type` | 列舉字串 |
| MULTI_SELECT (10) | `direction` / `checktype` / `showselectall` | 排列方向 / 勾選樣式 / 全選開關 | 列舉字串 |
| DATE (15) | `showtype` | 日期精度（DATE 預設 `"3"`；DATE_TIME 預設 `"1"`） | 列舉字串 |
| RELATE_SHEET (29) | `showtype` | 顯示：`"1"`=卡片 `"2"`=列表 `"3"`=下拉框 `"5"`=表格 `"6"`=標籤頁表格 | 列舉字串 |
| RELATE_SHEET (29) | `allowlink` / `searchrange` / `scanlink` / `scancontrol` | 開啟記錄連結、搜尋範圍、掃碼關聯開關 | `"0"`\|`"1"` |
| RELATE_SHEET (29) | `coverid` | 卡片封面欄位 | controlId 字串 |
| RELATE_SHEET (29) | `bidirectional` | 雙向關聯標誌 | `"0"`\|`"1"` |
| SUB_LIST (34) | `allowadd`/`allowedit`/`allowcancel`/`allowcopy`/`allowimport`/`allowexport`/`allowbatch` | 內聯行的逐操作開關 | `"0"`\|`"1"` |
| SUB_LIST (34) | `enablelimit` / `min` / `max` | 行數限制 | `"0"`\|`"1"`、數字字串 |
| SUB_LIST (34) | `controlssorts` | 可見子列順序 | controlId 的 JSON 陣列（字串） |
| SWITCH (36) | `showtype` | 檢查框顯示變體 | 列舉字串 |
| SCORE (28) | `itemnum` / `itemtype` | 等級數 / 圖示型別 | 數字字串 |
| AUTO_ID (33) | `increase` | 編號規則 | JSON 字串 `[{type,repeatType,start,length,format}]` |
| ATTACHMENT (14) | `showtype` / `covertype` / `allowupload` / `allowdelete` / `allowdownload` / `alldownload` / `webcompress` | 畫廊或列表、封面、逐操作開關 | 列舉字串 / `"0"`\|`"1"` |
| 任意有預設值 | `defsource` | 預設值規則；靜態選項預設值還會同步置 `options[].checked` | JSON 字串 `[{cid,rcid,staticValue,…}]`，先讀後改 |
| TEXT (2) | `analysislink` / `sorttype` | URL 自動轉連結 / 排序規則 | `"0"`\|`"1"`、`"en"` |
| MOBILE_PHONE (3) | `defaultarea` / `commcountries` | 預設國別 / 允許的國別集 | JSON 字串 |

選項集層面另有 `colorful`（啟用選項顏色，顏色本體在 `options[].color`）與
`enableScore`（啟用選項分值）兩個布林開關。

### 4. FieldSpec — `--fields` 高層方言的鍵

`worksheet create --fields` / `update-fields --fields` 每項接受的鍵
（snake_case 與對應 camelCase 同義，二選一）：

| 鍵 | 含義 | 值形態 |
|---|---|---|
| `type` | 必填；整數、型別名或 CODE（見 §1） | int \| string |
| `name` | 必填；欄位顯示名 | string |
| `required` / `unique` | 必填 / 唯一 | bool |
| `hint` | 佔位提示 | string |
| `options` | 選項（type 9/10/11）；字串自動展開成帶顏色/key 的選項物件 | `["a","b"]` 或完整選項物件陣列 |
| `data_source` / `dataSource` | 型別專屬橋接（語義同 WireControl `dataSource`；SHEET_FIELD/SUBTOTAL 只傳裸 controlId，`$…$` 包裹自動完成） | string |
| `source_control_id` / `sourceField` | SHEET_FIELD/SUBTOTAL 的目標列 | controlId 字串 |
| `show_controls` / `showFields` | RELATE_SHEET/SUB_LIST 展示的關聯欄位 | controlId 的 JSON 陣列 |
| `relation_controls` / `relationControls` | SUB_LIST 掛載已有表模式：目標表完整控制元件列表 | 控制元件物件陣列，先讀後改 |
| `child_fields` / `childFields` | SUB_LIST 內聯新建子表（推薦）：子欄位的 FieldSpec 列表 | FieldSpec 的陣列（遞迴同形） |
| `multi` | RELATE_SHEET：`true`=多條 `false`=單條 | bool |
| `is_title` / `isTitle` | 標為標題欄位（通常用命令級 `--title-name` 代替） | bool |
| `row` / `col` / `size` | 顯式網格位置/跨度；不傳則自動流式佈局（半寬兩列一行） | int |
| `layout` | `{span: 3|6|12}`，等價於 `size` | 物件 |
| `config` | RELATE_SHEET 便捷塊：`displayMode`(`"dropdown"`/`"card"`=單條，`"inlineTable"`/`"tabTable"`=多條)、`showFields`、`coverField`、`bidirectional` | 物件 |
| `defaultValue` | 高層預設值**陣列**（不是單個物件），自動轉 `advancedSetting.defsource`。每項 `{source, …}`：`{source:"static", value}`、`{source:"field", field}`、`{source:"relation", relationField, field}`（`relationField` 是關聯欄位、`field` 是取關聯記錄上的哪一列）、`{source:"system", value}`（`value` 取 `currentUser` / `now` / `currentLocation`）。source 寫成別的會被整項丟掉 | 陣列 |
| `advanced_setting` / `advancedSetting` | 直寫 advancedSetting 子鍵（見 §3） | 字串值的物件 |
| `extra` | 逃生口：合併進最終控制元件的任意原始鍵 | 物件（WireControl 鍵） |

只讀輸出鍵（`id`、`alias`、`subType`、`precision`、`max`、`unit`、`desc`、`remark`、
`isReadOnly`、`isHidden`、`isHiddenOnCreate`、`sourceType`、`relation`）在寫入時會被自動忽略。

`worksheet fields` 的預設輸出**可以原樣回傳 `--fields`**，不需要任何手工清洗：空的
`dataSource` / `sourceField` 會被忽略，選項鍵統一是 `isDeleted`，顏色和分值原樣保留。

```bash
hap --json worksheet fields <工作表ID> > layout.json
# 编辑 layout.json
hap worksheet update-fields <工作表ID> --fields @layout.json --check
hap worksheet update-fields <工作表ID> --fields @layout.json
```

要位元組級控制 `advancedSetting` 時改走 `--raw` + `--controls`（原樣下發，不做任何翻譯）。
注意**非空**的 `dataSource` 放在不接受它的型別上仍會報錯——那是真的用錯了，不是往返問題。

其中 `isReadOnly` / `isHidden` / `isHiddenOnCreate` 是**算出來的真實值**（由
`fieldPermission` 與 `controlPermissions` 按位與得出，見 §2），可以據此判斷某個欄位在表單裡
到底是不是被隱藏或鎖定；`relation.bidirectional` 同理，`null` 表示查不出而不是「不是雙向」。

### 5. 同一個數字在不同位置意思不同

- 欄位型別 `2` 是文字；關聯欄位的 `sourceControlType: 2` 表示這是個關聯；導航顯示狀態 `2` 是全隱藏。
  用 `--visibility hidden` 這種名字就不用記該填哪個 `2`。
- `enumDefault` / `enumDefault2` **每種欄位型別含義都不一樣**，不要把在某個型別上試出來的值
  套到別的型別上（見 §2 的分型別說明）。
