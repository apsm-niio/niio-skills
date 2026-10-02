---
name: hap-cli-app-editor
description: 用 niio CLI 命令列工具（CLI）修改一個已存在的 niio 應用裡的某個具體元素時用本 skill。只要使用者說「在某表加個欄位」「把這個檢視改名」「修改工作流」「給某角色加權限」之類、針對已有應用做單點區域性修改，就觸發。不觸發：增刪改業務記錄、查詢資料、寫調 niio CLI 的程式碼；從零搭整個新應用請改用 hap-mcp-app-builder。
---
> **對外表達規範**：對使用者的說明、提示與成果摘要，統一使用 niio 品牌及台灣繁體中文。執行所需的技術名稱、套件、命令、API 參數與路徑請保留；只在操作或除錯所需的程式碼中呈現，勿將它們用作產品標題或品牌名稱。


# niio 應用編輯器（細粒度元素 CRUD）

你對一個**已存在**的 niio 應用做精確的區域性修改：增、刪、改單個元素（工作表 / 欄位 / 檢視 / 角色權限 / 自訂動作 / 工作流與節點 / 自訂頁面與元件 / 應用與分組）。 如果是要增刪改業務資料，請遵從 `hap-cli` 主 Skill 直接呼叫 `hap` 命令.

## 核心模型：兩個入口，按危險度分流

**預設入口是裸 `hap` 命令** —— 絕大多數元素編輯就是一條命令：

```bash
hap worksheet view update <ws_id> <view_id> --name "進行中的訂單"
hap workflow publish <process_id>
hap app role add-member <role_id> --user-ids <account_id> -a <app_id>
```

**只有三類編輯走 edit-spec（`hap app-editor`）**，因為它們的安全寫法是「讀出整體 → 改一處 → 整體寫回」，徒手做容易靜默丟資料：

| 編輯物件 | edit-spec op | 為什麼不能裸做 |
|---|---|---|
| **已有欄位**的修改/刪除/重排 | `field.update` / `field.delete` / `field.reorder` | 必須整表控制元件集寫回，否則系統反向控制元件會被靜默丟掉 |
| **頁面元件**增刪改 | `component.add` / `component.update` / `component.delete` | 頁面佈局是一個整體 components 陣列，必須讀改寫 |
| **動作按鈕**新建/修改 | `custom-action.create` / `custom-action.update` | 高層 action_spec 自動翻譯成按鈕設定並接好關聯流程 |

（新增欄位 `field.add` 也在 edit-spec 裡，與其他 field op 用同一份寫法。）其餘一切元素——工作表、檢視、角色、工作流、節點、頁面本身、應用與分組——**直接用命令**，各模組的命令與參數字典見下方索引。

## 前置條件

1. **登入**：`hap auth whoami` 確認已登入且選好組織；未登入讓使用者先 `hap auth login`。
2. **管理員權限（硬性前提）**：編輯應用元素要求當前使用者對該應用有管理權限。動手前用 `hap app list-managed` 確認目標 app 在清單裡；不在則**不要硬試**，告知使用者需要管理員授權或換帳號登入。
3. 上下文中沒有 appId 時，讓使用者提供應用名或 appId。

## 通用工作流（4 步）

1. **Inspect**：`hap app-editor inspect <appId或應用名>` 列印應用的「邏輯名 → id」全結構（工作表、檢視、角色、工作流、頁面、分組…）。後續命令要的各種 id 都從這裡拿；更細的 id 用各模組的 list/info 命令。
2. **Read**（改複雜值前必做）：**先用讀命令匯出現狀，在真實結構上改，再寫回**。
   - 檢視：`hap --json worksheet view info <ws_id> <view_id>`
   - 節點：`hap --json workflow node get <process_id> <node_id>`
   - 欄位：`hap --json worksheet fields <ws_id> --raw`
   - 頁面：`hap --json custom-page info <page_id>`（參數是頁面 id）
   字典沒覆蓋的鍵，以讀到的實際結構為準——照形改寫永遠是安全的。
3. **Edit**：按模組文件的呼叫正規化執行命令；或對三類 edit-spec 編輯：寫 spec → `hap app-editor validate <spec.json>`（純本地）→ `plan`（dry-run 預演）→ `apply`。
4. **Verify**：用對應讀命令確認改動生效。

## 🚨 六個「回傳成功但其實沒做對」的坑

niio 的寫介面大量存在「照樣回傳成功、資料卻是錯的」，所以第 4 步 Verify 不是可選項：

1. **`update-fields` 是整表替換**——沒傳的列連同資料一起刪掉；條目不帶 `id` 會被當成新列重建。
   給已有表加列一律用 `add-fields` 或 `field.add`。儲存前先 `--check`，儲存後看自動回讀的報告。
2. **自造 `controlId`** 會建出在表格和關聯控制元件裡永遠讀不出值的空白列。新建欄位一律省略它。
3. **選項/地區傳了不存在的值**不會報錯，會寫進一個無效值，介面顯示空白（詳見 `hap guide record`）。
4. **`--view-id` 撤動作按鈕**只對「限定了顯示檢視」的按鈕有效；全檢視按鈕會明確報錯，不會假裝撤下。
5. **工作流建完不等於建好**——觸發器沒綁、`fill_in` 沒有可編輯欄位，只有 `workflow publish` 會告訴你。
   加完節點順手發一次。
6. **複製工作表**時沒被 `--keep-relation` 點名的關聯/子表/級聯列會變成純文字，且沒有任何提示。

## 值形態約定（讀字典表時）

各模組字典表的「值形態」列分三檔：
- **標量/列舉**：可取值直接寫在格內，如 `"1"=顯示 "2"=隱藏`；
- **簡單結構**：一行描述，如 `controlId 的 JSON 陣列`；
- **複雜結構**：連結到 [scripts/types/](scripts/types/) 下的型別定義（schema + 可直接套用的示例），全 skill 每個結構只定義一次：

| 型別 | 用在哪 |
|---|---|
| [FilterCondition](scripts/types/filter-condition.schema.json) | 檢視篩選、業務規則、按鈕 enableWhen、圖表篩選、頁面篩選元件的儲存形態（讀回時看到的）；寫入時優先用統一篩選寫法 `{logic, items:[{field, op, value}]}`，見 `hap guide record filter` |
| [SortItem](scripts/types/sort-item.schema.json) | 檢視多重排序、工作流節點 sorts |
| [WireControl](scripts/types/wire-control.schema.json) | 欄位的原始控制元件物件（讀寫通用貨幣） |
| [OperateCondition](scripts/types/operate-condition.schema.json) | 工作流節點/分支條件（**不是** FilterCondition，欄位名是 `filedId`） |
| [WorkflowAccounts](scripts/types/workflow-accounts.schema.json) | 工作流收件人（type 語義反直覺，必讀） |
| [WorkflowFieldWrite](scripts/types/workflow-field-write.schema.json) | 資料節點欄位寫入（`$nodeId-fieldId$` 動態模板） |

一個典型的 niio 工作表檢視頁面地址：`/app/<app_id>/<section_id>/<worksheet_id>/<view_id>`。一個典型的 niio 工作表行記錄頁面地址：`/app/<app_id>/<worksheet_id>/<view_id>/row/<rowid>`。

## 模組文件索引

按要操作的元素**只讀對應那一份**（每份 = 呼叫正規化 + 資料字典）：

- [references/worksheets-and-fields.md](references/worksheets-and-fields.md) — 工作表、欄位（含 field edit-spec 寫法）
- [references/views.md](references/views.md) — 檢視（editAttrs / advancedSetting 全字典）
- [references/roles.md](references/roles.md) — 角色、權限、成員
- [references/workflows.md](references/workflows.md) — 自動化工作流與節點基礎
- [references/nodes.md](references/nodes.md) — 節點設定深度字典（8 類高頻節點）
- [references/custom-actions.md](references/custom-actions.md) — 動作按鈕（action_spec / wire 兩種寫法）
- [references/custom-pages.md](references/custom-pages.md) — 自訂頁面與元件（含 component edit-spec 寫法）
- [references/application.md](references/application.md) — 應用本身與導航分組
- [references/charts.md](references/charts.md) — 統計圖（改已有的圖；規格本體見 `hap guide chart`）
- [references/edit-spec.md](references/edit-spec.md) — edit-spec 信封與三類 op 的完整語義

**多元素聯動場景**（一個目標要串多條命令）見 [references/scenarios/](references/scenarios/)，每個場景一份文件，含命令順序與 id 傳遞。三類 edit-spec 的可直接套用樣例在 [examples/](examples/)（field / component / custom-action 各一份）。

## 邊界與紀律

- 只改使用者明確要求的元素。
- 破壞性操作：edit-spec 的刪除類 op 必須帶 `"confirm": true`；裸命令的刪除類一律帶 `--yes/-y` 二次確認，不傳 `-y` 時會互動式詢問（非互動環境下直接中止）。`-y` 只是跳過提示，不等於授權——任何刪除動手前都先取得使用者明確同意。刪完用 `hap app trash -a <appId>` 核對：工作表 / 自訂頁 / AI 助手預設都是進應用回收站，在回收站裡看到它才說明刪成功了。
- 不猜參數：字典 + 讀命令匯出的現狀是唯一依據；兩者衝突時以讀到的為準。
- **`hap-cli` 會自動升級，命令和選項會變。** 本 skill 的字典核對於 0.9.0，只是加速器，不是權威：
  動手前用 `hap <命令> --help` 核准確參數，用 `hap guide worksheet` / `hap guide workflow` /
  `hap guide chart` / `hap guide record` 核值形態與陷阱——它們隨本機裝的那一版走，永遠不會過期。
  與本 skill 衝突時以它們為準。
- 整應用從零生成不屬於本 skill —— 用 hap-mcp-app-builder。
