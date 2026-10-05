# 自訂頁面與頁面元件

## 呼叫正規化

```bash
# 頁面生命週期（第一個參數都是應用 id）
hap custom-page create <appId> "資料看板" --section-id <sectionId> --icon chart
hap custom-page rename <appId> <pageId> --section-id <sectionId> --name "新名字"
hap custom-page copy   <appId> <pageId> --section-id <sectionId> -n "看板副本"
hap custom-page delete <appId> <pageId> --section-id <sectionId> -y

# 讀頁面佈局 —— 注意：這裡的參數填【頁面 id】，不是應用 id
hap custom-page info <pageId>
# 🚨 傳成應用 id 不會報錯：它回傳一個 version:0、components:[] 的空殼。
#    別把這個空殼當成「頁面沒有元件」——照它整頁寫回會把真元件全清掉。
#    讀到 version 為 0 且 components 為空時，先確認自己傳的是不是頁面 id。

# 元件型別對照表
hap custom-page component-types

# 改頁面描述/設定（參數也是頁面 id）
hap custom-page update-config <pageId> --desc "運營週報看板"
```

### 往頁面上放一張統計圖

圖表**不是**在頁面裡建的：先在工作表上建圖拿 `reportId`，再把它作為元件擺到頁面上。

```bash
# 1) 建圖。--page-id 讓這張圖歸屬該自訂頁，而不是算進工作表自己的統計清單
hap worksheet chart create <worksheetId> --name "各狀態金額" --report-type 1 \
  --page-id <pageId> -j '{...圖表規格...}'

# 2) 讀目前 version 和已有元件
hap --json custom-page info <pageId>

# 3) 整頁寫回（把新元件追加進原有 components 一起提交）
hap custom-page save <pageId> --version <目前version> --components '[...]'
```

圖表元件的必備形狀：

```jsonc
{"type": 1, "value": "<reportId>", "worksheetId": "<worksheetId>",
 "name": "各狀態金額", "reportType": 1,
 "config": {"objectId": "<32位十六進位制隨機串>"},
 "web": {"title": "", "titleVisible": false, "visible": true,
         "layout": {"x": 0, "y": 0, "w": 24, "h": 10, "minW": 2, "minH": 4}},
 "mobile": {"title": "", "titleVisible": false, "visible": true, "layout": null}}
```

- 圖表元件 `type` 是 **1**，`value` 放 `reportId`，還**必須**帶 `worksheetId` 和 `reportType`。
- `config.objectId` 每個元件一個唯一 32 位十六進位制串（聯動篩選靠它定位）。
- 佈局是 **48 柵格**：`w` 最大 48，一行放兩張圖各 `w:24`。
- `--version` 必須等於頁面目前 version，否則報「自訂頁面儲存失敗」；存成功後 version +1。
- 篩選元件（`type=6`）可以內聯攜帶 `filtersGroup: {filters:[…]}`，CLI 會先存篩選組再把生成的 id
  替換進元件。這時需要 `--owner-app-id`（省略時自動從頁面的工作表元資料解析）。

圖表規格本身（`xaxes` / `yaxisList` / `filter` / reportType 取值）見 `hap guide chart`。
**一張圖沒有 `filter` 塊也能儲存成功，但頁面上一片空白**——新建時 CLI 會自動補「全部時間」的預設
範圍，所以 `chart create` 已不會空白；但 `chart update` **不補**（否則會覆蓋這張圖原本的時間範圍），
所以改圖時只傳要改的項。

**元件增刪改推薦走 edit-spec**（`hap app-editor apply`）：頁面佈局是整體讀改寫——讀全量元件清單、改目標、整頁寫回；edit-spec 的 `component.add/update/delete` 幫你處理這套流程並按名字定位元件，其餘元件原樣保留。一次性示例：

```json
{
  "app": "<appId 或應用名>",
  "ops": [
    { "type": "component.add", "page": "資料看板",
      "component": { "name": "公告", "type": "richText", "value": "<p>歡迎</p>",
                     "layout": { "x": 0, "y": 0, "w": 48, "h": 5 } } },
    { "type": "component.add", "page": "資料看板",
      "component": { "name": "官網", "type": "embedUrl", "value": "https://example.com" } },
    { "type": "component.update", "page": "資料看板", "component": "公告",
      "set": { "value": "<p>已更新</p>" } },
    { "type": "component.delete", "page": "資料看板", "component": "官網", "confirm": true }
  ]
}
```

```bash
hap app-editor apply page-edit.json
```

低層備選是 `hap custom-page save`，但它**要求傳完整 components 陣列**——漏掉的元件會被刪除：

```bash
# 先 info 拿 version 和現有 components，改完整體寫回
hap custom-page save <pageId> --version <N> --components '[ ...全量元件... ]'
```

坑位提示：

- `info` / `save` / `update-config` 的位置參數是**頁面 id**；`create` / `rename` / `copy` / `delete` 的第一個參數才是應用 id。混填會讀到空或報錯。
- `save` 必須帶 `info` 回傳的 `version`；`components` 是整頁佈局的全量替換，不是增量。
- filter 元件（type=6）可以內聯高層 `filtersGroup`（含 `filters[]`），儲存時會先落成儲存物件再替換為 id；這條路徑需要 `--owner-app-id <appId>`（預設時會嘗試自動解析）。
- 元件的顯示名存在 `web.title`，讀回的元件**沒有頂層 name**——按名字找元件要看 `web.title`。
- richText 的 `value` 是 HTML 字串；embedUrl / image 的 `value` 是 URL。資料繫結型元件（chart 要 reportId、view 要 worksheetId/viewId、filter 要 filtersGroup）用 `raw:{<wire 鍵>}` 直接給 wire 物件（最後合併、優先生效）。

## 資料字典

字典生成於 2026-06-10；未覆蓋的鍵以讀命令回傳的實際結構為準。

### 元件型別（type 可寫名字或整數）

| 名字 | 數值 type | 含義 | 預設尺寸 (w×h) |
|---|---|---|---|
| analysis / chart | 1 | 統計圖表 | 24×10 |
| richText | 2 | 富文字 | 48×5 |
| embedUrl | 3 | 嵌入網址 | 24×12 |
| button | 4 | 按鈕 | 24×6 |
| view | 5 | 檢視 | 48×12 |
| filter | 6 | 篩選器 | 24×3 |
| image | 8 | 圖片 | 24×12 |
| carousel | 9 | 輪播 | 24×8（通用預設） |
| tabs | 10 | 標籤頁容器 | 24×8（通用預設） |
| card | 11 | 卡片容器 | 24×8（通用預設） |

### 元件通用鍵（wire 形態，info 回傳 / save 提交）

| 鍵 | 含義 | 值形態 |
|---|---|---|
| type | 元件型別 | int（見上表） |
| value | 元件值（richText=HTML，embedUrl/image=URL，chart=reportId，filter=filtersGroupId） | string |
| web | PC 端展示塊 | `{title, titleVisible, visible, layout}` |
| web.title | **元件顯示名**（按名定位元件以此為準） | string |
| web.layout | 48 列柵格位置 | `{x, y, w, h, minW, minH}` |
| mobile | 移動端展示塊 | 同 web 結構；layout 可為 null |
| filtersGroup | （filter 元件）內聯高層篩選定義，儲存時換成 id | `{filters: → [FilterCondition[]](../scripts/types/filter-condition.schema.json)}` |

### edit-spec 元件簡潔形態（component.add 的 component）

| 鍵 | 含義 | 值形態 |
|---|---|---|
| name | 元件名（寫入 web.title） | string |
| type | 元件型別 | 名字或整數（見上表） |
| value | 元件值 | string（按型別語義） |
| layout | 柵格位置，預設按型別給預設尺寸 | `{x, y, w, h}` 一層物件 |
| raw | wire 鍵逃生口，最後合併覆蓋 | object（按 wire 通用鍵） |

### 頁面級選項速查

| 鍵/選項 | 含義 | 值形態 | 適用 |
|---|---|---|---|
| --section-id | 頁面所在導航分組 | string | create/rename/copy/delete 必填 |
| --icon | 圖示名 | string | create/rename |
| --remark | 描述 | string | create |
| --create-type | 建立型別，1=外鏈頁面 | int | create |
| --url-template | 外鏈地址模板 | string | create/rename |
| --permanently | 徹底刪除；不加就進應用回收站，用 `hap app trash` 能看到也能還原 | flag | delete |
| --version | 佈局版本號（info 可得） | int | save 必填 |
| --adjust-screen | 適配螢幕 | flag 對 | save/update-config |
| --url-params | URL 參數描述符 | JSON array | save/update-config |
| --config | 頁面設定 | JSON object | save/update-config |
