# 能力歸屬矩陣（MCP 建立 vs CLI 精修）

> 本表是「何時把活交給 CLI」的唯一事實來源。Step 12（`steps/12_cli_refinement.md`）
> 末尾對賬時，依據本表的 **CLI-only 硬缺口** 列識別 MCP 沒做到、需用 `hap` CLI 回填的項。
>
> **MCP 列**來自本構建器各 step 實際呼叫的工具（builder 用到即證明該工具存在，是 MCP 表面的可靠下界）。
> **CLI 列**來自 `hap` 命令表面（細粒度編輯能力，對應 app 編輯相關命令族）。
>
> ⚠️ **校準須知**：標 `🔶待校准` 的格子，需用niio MCP server 的真實工具 schema 複核
> （例如 `create_view` 的 payload 到底能不能表達某配置項）。在拿到真實 schema 前，這些按
> 「MCP 可能做不到 → 暫列為硬缺口候選」從嚴處理，寧可 Step 12 多查一次，也不要漏。

## 圖例

- `MCP` —— MCP 工具能做，建構走 MCP，Step 12 不介入
- `CLI-only` —— MCP 做不到的**硬缺口**，進入 Step 12 `cliGaps[]` 由 CLI 回填
- `both` —— 兩邊都能做；預設走 MCP，不雙寫
- `🔶待校准` —— 歸屬取決於 MCP 真實 schema，暫從嚴當硬缺口候選

---

## 1. 應用與導航

| 物件/操作 | MCP 工具 | CLI 能力 | 歸屬 | Step 12 檢查點 |
|---|---|---|---|---|
| 建立應用 | `create_app` | `hap app` 系 | MCP | — |
| 建立導航分組/項 | `create_app_sections` / `create_app_items` | application 模組命令 | MCP | — |
| 修改應用屬性/分組（建後） | （無 update 工具） | application 模組命令 | CLI-only | 一般不需要；僅當 plan 要求建後調整分組順序/圖示且 MCP 沒表達時 |

## 2. 工作表與欄位

| 物件/操作 | MCP 工具 | CLI 能力 | 歸屬 | Step 12 檢查點 |
|---|---|---|---|---|
| 建立工作表 | `create_worksheet` | worksheets 模組 | MCP | — |
| 讀取欄位結構 | `get_worksheet_structure` | `hap worksheet fields --raw` | both | — |
| 建表時的欄位集 | `create_worksheet`（隨表建欄位） | field edit-spec | MCP | — |
| **特殊欄位型別**（`create_worksheet` 不支援的型別） | 🔶待校準 | field.add (edit-spec) | 🔶待校準 → CLI-only 候選 | 對賬：plan 期望欄位型別 vs 實建欄位型別，缺失/降級的用 CLI 補 |
| **建後改欄位**（改配置/刪/重排） | （無欄位級 update 工具） | field.update/delete/reorder | CLI-only | 僅當 plan 要求建後調整既有欄位時 |

## 3. 自訂動作（按鈕）

| 物件/操作 | MCP 工具 | CLI 能力 | 歸屬 | Step 12 檢查點 |
|---|---|---|---|---|
| 建立動作 | `batch_create_custom_actions` / `create_custom_actions` | custom-actions 模組 | MCP | — |
| 動作高階配置（enableWhen 等 `create` 未表達項） | 🔶待校準 | custom-action.create/update (action_spec) | 🔶待校準 → CLI-only 候選 | 對賬：plan 動作的觸發條件/可見性 vs 實建配置 |

## 4. 檢視（重點硬缺口區）

| 物件/操作 | MCP 工具 | CLI 能力 | 歸屬 | Step 12 檢查點 |
|---|---|---|---|---|
| 建立檢視（含 step 5 已列的豐富配置） | `create_view` | views 模組 | MCP | — |
| **建後改檢視**（改名/改篩選/改列…） | （無 `update_view` 工具） | `hap worksheet view update` | CLI-only | 僅當 plan 要求建後調檢視時 |
| **檢視高階配置**（`create_view` payload 表達不出的 editAttrs/advancedSetting 項） | 🔶待校準 | views editAttrs/advancedSetting 全字典 | 🔶待校準 → CLI-only 候選 | 對賬：plan 檢視期望的增強配置（color/group/filterList/封面等）vs 實建檢視，缺的用 CLI 補 |

> 檢視是最可能產生硬缺口的物件：MCP 只有 `create_view`，沒有 update；凡 `create_view` 一次沒配上的，
> 之後只能 CLI 補。校準時重點核對 `create_view` 到底吃哪些配置鍵。

## 5. 自訂頁面與元件

| 物件/操作 | MCP 工具 | CLI 能力 | 歸屬 | Step 12 檢查點 |
|---|---|---|---|---|
| 建立頁面空殼 | （隨 5b，create_custom_page 類） | custom-pages 模組 | MCP | — |
| 配置頁面元件 | `update_custom_page` | component edit-spec | both | — |
| **元件細配置**（`update_custom_page` 未表達項） | 🔶待校準 | component.add/update/delete | 🔶待校準 → CLI-only 候選 | 對賬：plan 頁面元件 vs 實建元件 |

## 6. AI 助手（chatbot）

| 物件/操作 | MCP 工具 | CLI 能力 | 歸屬 | Step 12 檢查點 |
|---|---|---|---|---|
| 建立 AI 助手 | `create_chatbot` | （CLI chatbot 相關） | MCP | — |
| 角色對 AI 助手的訪問權 | （`create_role` 無 chatbots 欄位） | role set-chatbots | CLI-only | 對賬：plan 角色應可訪問的 AI 助手 vs 實際角色許可權（已知歷史缺口） |

## 7. 角色與許可權

| 物件/操作 | MCP 工具 | CLI 能力 | 歸屬 | Step 12 檢查點 |
|---|---|---|---|---|
| 建立角色 | `create_role` | roles 模組 | MCP | — |
| **細粒度許可權/成員/AI助手權** | （`create_role` 表達有限） | roles 許可權/成員/set-chatbots | CLI-only | 對賬：plan 角色許可權矩陣 vs 實建角色（尤其 AI 助手訪問權，見 §6） |

## 8. 工作流與節點（重點硬缺口區）

| 物件/操作 | MCP 工具 | CLI 能力 | 歸屬 | Step 12 檢查點 |
|---|---|---|---|---|
| 建立工作流 | `create_process` | workflows 模組 | MCP | — |
| 批次建節點 | `batch_create_process_nodes` | nodes 模組 | MCP | — |
| 讀工作流結構 | `get_workflow_structure` | `hap workflow node get` | both | — |
| 刪節點/流程 | `delete_process_node` / `delete_process` | nodes/workflows 模組 | both | — |
| 釋出 | `publish_process` | `hap workflow publish` | both | — |
| **建後改既有節點配置** | （無節點 update 工具） | nodes 深度字典（8 類節點） | CLI-only | 僅當 plan 要求建後微調既有節點時 |
| **節點深配置**（`batch_create_process_nodes` 表達不出的欄位） | 🔶待校準 | nodes.md 深度字典 | 🔶待校準 → CLI-only 候選 | 對賬：plan 節點設計意圖 vs 實建節點配置 |

## 9. 業務資料（示例資料）

| 物件/操作 | MCP 工具 | CLI 能力 | 歸屬 | Step 12 檢查點 |
|---|---|---|---|---|
| 批次寫記錄 | `batch_create_records` / `add_record` | `hap worksheet record ...` | MCP | — |
| 讀/改/刪記錄 | `list_records`/`get_record_list`/`update_record`/`delete_record` | record 模組 | both | — |

> 資料不是結合重點：MCP 資料工具齊全，Step 12 不介入示例資料。

---

## CLI-only 硬缺口清單（Step 12 對賬主目標）

按"最可能真實存在硬缺口"優先順序排序（校準後據實增刪）：

1. **檢視增強配置**（§4）— `create_view` 表達不出的 color/group/filterList/封面/quickActions 等，建後只能 CLI 補。
2. **角色 → AI 助手訪問權**（§6/§7）— `create_role` 無 chatbots 欄位，已知歷史缺口，必查。
3. **角色細粒度許可權/成員**（§7）。
4. **工作流節點深配置**（§8）— `batch_create_process_nodes` 表達不出的節點欄位。
5. **動作按鈕高階配置**（§3）— 觸發條件/可見性。
6. **特殊欄位型別**（§2）— `create_worksheet` 不支援的欄位型別。
7. **頁面元件細配置**（§5）。

## 待校準事項（需niio MCP server 真實工具 schema）

- `create_view` 實際接受的配置鍵全集 → 決定 §4 哪些是真硬缺口。
- `create_worksheet` 支援的欄位型別全集 → 決定 §2「特殊欄位型別」範圍。
- `batch_create_process_nodes` 的節點配置欄位全集 → 決定 §8 節點深配置缺口。
- `create_role` / `update_custom_page` / `create_custom_actions` 的 payload 全集 → 決定 §3/§5/§7 缺口。

> 校準方式：拿到 MCP server 工具 schema 後，逐項把 `🔶待校准` 改判為 `MCP`（能表達）或 `CLI-only`（確為硬缺口），並據此精簡上面的硬缺口清單。
