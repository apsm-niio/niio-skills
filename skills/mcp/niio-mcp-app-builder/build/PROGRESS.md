# Progress 狀態機

`hap-context.json` 中的 `progress` 欄位是一個有限狀態機。**所有 progress 寫入均由排程器完成**，各 step 只負責寫入自己的產出資料（ID 對映等），不寫 progress。

## 狀態定義

| 狀態值 | 含義 | 前置狀態 | 寫入時機 |
|--------|------|---------|----------|
| _(空/不存在)_ | 初始狀態 | — | — |
| `app_created` | 應用和導航分組已建立 | _(空)_ | Step 1 完成後 |
| `worksheets_created` | 所有工作表已建立 | `app_created` | Step 2 完成後 |
| `fields_refreshed` | 欄位結構已重新整理 | `worksheets_created` | Step 3 完成後 |
| `actions_created` | 自訂動作已建立 | `fields_refreshed` | Step 4 完成後 |
| `views_created` | 檢視已建立 | `actions_created` | Step 5 完成後 |
| `sample_data_created` | 示例資料已寫入 | `views_created` | Step 5 和 Step 6 都完成後 |
| `page_shells_created` | 頁面空殼與 AI 助手已建立 | `sample_data_created` | Step 5b 完成後 |
| `config_completed` | 頁面元件 + 角色 + 工作流設計全部完成 | `page_shells_created` | Step 7、Step 8、Step 9 全部完成後 |
| `workflows_deployed` | 系統工作流 + 自訂動作工作流均已釋出 | `config_completed` | Step 10 和 Step 11 都完成後 |
| `completed` | 全部完成（含 CLI 建後精修對賬） | `workflows_deployed` | Step 12 完成後 |
| `failed` | 執行失敗 | _(任意)_ | 任意步驟失敗時 |

> **並行匯合點**：`page_shells_created` → `config_completed` 之間，Step 7/8/9 三路並行。排程器內部追蹤各路完成狀態，三路全部完成後才寫入 `config_completed`。

## 規則

- **只能前進不能後退**——每步只能將 progress 推進到下一個狀態
- **不能跳躍**——不允許從 `app_created` 直接跳到 `views_created`
- **failed 是終態**——進入 `failed` 後必須人工介入
- **排程器獨佔寫入**——各 step 不寫 progress，由排程器在驗證透過後統一寫入
- **並行匯合由排程器追蹤**——並行步驟各自完成後排程器在記憶體中記錄，全部完成才推進 progress
