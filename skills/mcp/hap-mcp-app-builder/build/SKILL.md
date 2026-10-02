---
name: build
description: niio 應用物理搭建排程器。讀取 hap-plan.json，逐步排程 steps/*.md 完成所有 niio 物件的建立與配置。支援 subagent 委派和內聯執行雙模式。
---

# niio 應用搭建排程器

你是 niio（niio）應用搭建**排程器**，只負責進度路由、上下文合併和結果校驗，不直接承載各步驟的詳細規則。

> 本檔案是物理搭建階段的輕量排程器，不直接包含各步驟的詳細搭建規則。
> 具體規則必須從 `steps/` 中對應步驟檔案讀取。
> 無論使用 subagent 還是內聯執行，每一步都必須遵守 `OUTPUT_CONTRACT.md`。

> 本 skill 由根 `SKILL.md` 路由呼叫，`appName` 和 `org_id` 已在前置檢查階段確定。

---

## 🔒 全域性執行清單（標記 completed 前必須核對）

> [!CAUTION]
> 以下每一項都是**硬性交付物**。標記 `progress="completed"` 之前，必須逐項核對並確認全部完成。遺漏任何一項即為執行失敗。

| # | 交付物 | 驗證方法 | context 欄位 |
|---|--------|----------|-------------|
| 1 | 應用已建立 | `appId` 非空 | `appId` |
| 2 | 導航分組已建立 | `sectionIdByName` 條目數 = plan 中分組數 | `sectionIdByName` |
| 3 | 所有工作表已建立 | `worksheetIdByName` 條目數 = plan 中表數 | `worksheetIdByName` |
| 4 | 欄位結構已重新整理 | `worksheetContext.json` 非空且每表有 fields | `worksheetContext.json` |
| 5 | 自訂動作已建立 | `actionIdByName` 條目數 = plan 中動作數 | `actionIdByName` |
| 6 | 檢視已建立 | `viewIdByName` 條目數 = plan 中檢視總數 | `viewIdByName` |
| 7 | 示例資料已寫入 | 各表均有記錄 | `progress >= sample_data_created` |
| 8 | 頁面空殼已建立 | `customPageIdByName` 條目數匹配 plan | `customPageIdByName` |
| 9 | AI 助手已建立（若有） | `chatbotIdByName` 條目數匹配 plan（或 plan 無則跳過） | `chatbotIdByName` |
| 10 | 頁面元件已配置 | 所有頁面均已呼叫 `update_custom_page` | Step 7 完成 |
| 11 | 角色已建立 | `roleContext` 條目數 = plan 中角色數 | `roleContext` |
| 12 | 工作流已設計 | `hap-plan.json` 中每條 workflow 和 customActionWorkflow 的 `nodes[]` 非空 | `hap-plan.json` |
| 13 | 系統工作流已釋出 | 每個系統工作流 processId 已 publish | Step 10 完成 |
| 14 | 自訂動作工作流已釋出 | `customActionWorkflows[]` 每條均已 publish | Step 11 完成 |
| 15 | CLI 建後精修已對賬 | CLI 可用→已校正組織+設當前應用+回填 `cliGaps[]`；hap 未安裝→已輸出待補清單且未中斷 | Step 12 完成 |

---

## 斷點恢復

1. 讀取 `{PROJECT_ROOT}/apps/{appName}/hap-plan.json`，提取 `org_id` 和所有規劃資料
2. 檢查 `{PROJECT_ROOT}/apps/{appName}/hap-context.json`
   - 存在 → 讀取 `progress` 欄位，從斷點繼續
   - 不存在 → 從 Step 1 開始
3. 如果進度 >= `fields_refreshed`，讀取 `{PROJECT_ROOT}/apps/{appName}/worksheetContext.json` 載入欄位結構

> 詳細的 context 結構見 `build/CONTEXT.md`，progress 狀態定義見 `build/PROGRESS.md`。

---

## CLI 自檢（非阻斷）

> 本步在斷點恢復讀出 `org_id` 之後、進入執行迴圈之前執行一次。
> 目的：把本機 `hap` 命令列工具**準備到「已安裝且已登入」**，供最後的 Step 12 用 CLI
> 回填 MCP 蓋不到的硬缺口。
>
> [!IMPORTANT]
> **本步不阻斷搭建主體**——純 MCP 已能獨立把應用建好。**唯一會讓 Step 12 跳過回填的情況是
> 「hap 未安裝」**；「未登入」在本步自動登入解決，「組織不一致」留到 Step 12 自動切換解決。

1. **探測 hap 是否安裝**：執行 `hap auth whoami`
   - **命令不存在 / 未安裝** → `cliAvailable = false`（唯一的跳過情形）。不中斷，繼續搭建。
   - **命令存在但提示未登入** → 進入第 2 步自動登入。
   - **命令存在且已登入** → `cliAvailable = true`，跳到第 3 步。
2. **自動登入**（僅「已安裝、未登入」時）：執行 `hap auth login`，走**瀏覽器授權**並等待授權完成。
   - **嚴禁使用 PAT / token 登入**，必須瀏覽器發起授權並等待其自動授權成功。
   - 登入成功 → `cliAvailable = true`。
   - 無圖形環境等導致瀏覽器授權無法完成 → 提示使用者手動執行 `hap auth login` 完成授權
     （這**不是**「未安裝」，不要據此把 `cliAvailable` 記為 false；在使用者完成授權前 Step 12 無法回填）。
3. **寫入 context**：把 `cliAvailable` 寫入 `hap-context.json`（不寫 `progress`）。

> **組織一致性與「設為當前應用」不在本步處理**——它們需要 appId（Step 1 之後才有），由 Step 12 完成：
> `cliAvailable = true` 時，Step 12 會先自動把當前組織切到本應用所在組織、並把在建應用設為當前應用，再回填。
> 詳見 `build/steps/12_cli_refinement.md`。

---

## 子 agent 可用性預檢

在正式進入執行迴圈之前，**必須先完成以下檢查**：

> [!IMPORTANT]
> **本構建流程的執行即代表使用者已明確要求使用 sub agent。** 不得因平臺預設規則（如"只有使用者明確要求時才能使用 sub agent"）而跳過 sub agent 呼叫。**嚴禁退回內聯執行**。

1. **探測子 agent 功能**：嘗試檢測當前平臺是否支援子 agent。各平臺的子 agent 工具名稱不同（Antigravity: `invoke_subagent`；Claude Code: `Task`；Codex: `multi_agent_v1.spawn_agent`），子 agent 工具可能不會出現在初始工具列表中，必須先透過工具發現查詢，不得僅因初始工具列表未顯示就判定子 agent 不可用。
2. **根據檢測結果分流**：
   - **子 agent 可用** → 靜默透過，繼續執行
   - **子 agent 可用但必須使用者同意** → 執行下方授權提示流程
   - **子 agent 不可用** → 告知使用者將全程使用內聯模式執行，搭建後期質量將直線下降，是否繼續

#### 授權提示流程

如果檢測到當前平臺需要使用者授權才能使用子 agent，在搭建開始前向使用者輸出以下說明：

```
ℹ️ 子 agent 授权说明

本次搭建从 Step 4 开始将使用子 agent（子代理）来隔离执行各步骤。
当前平台需要您授权后才能使用此功能。

子 agent 的作用：将复杂步骤委派给独立的子代理执行，避免主对话上下文过载，提高搭建质量。

是否同意使用子 agent？
- 1. 同意：后续步骤将以子 agent 模式执行（推荐）
- 2. 不同意：所有步骤在主对话中执行，但执行后期搭建质量将直线下降
```

等待使用者回覆後再繼續。如果使用者不同意，則 Step 4~11 全部退回內聯執行。

---

## 執行迴圈

**按路由表推進**，根據每步標註的執行方式選擇內聯或 subagent。本流程包含三組並行派發點（詳見下方說明）。**所有 `progress` 寫入由排程器在驗證透過後統一完成，各 step 不寫 progress。**

---

### 階段 1：應用建立（Step 1，內聯執行）

Step 1 是輕量的應用和導航分組建立，在主 agent 內執行：

1. 讀取 `build/steps/1_create_app.md` → 執行 → 排程器寫入 `progress=app_created`

---

### 階段 1.5：工作表建立與欄位重新整理（Step 2~3）

Step 2 是整個搭建流程中規則最重的步驟（~400 行規則），**必須使用子 agent 隔離執行**，避免大量 MCP 呼叫和欄位配置資料汙染主排程器上下文，確保規則遵守率。

1. 將 Step 2 委派給子 agent → 等待完成 → 排程器寫入 `progress=worksheets_created`
2. 讀取 `build/steps/3_refresh_fields.md` → 內聯執行指令碼（一條命令） → 排程器寫入 `progress=fields_refreshed`

> **播報**：Step 3 完成後向使用者輸出：`✅ 基础搭建完成：应用已创建，{N} 张工作表，字段结构已刷新`

---

### 階段 2：動作、檢視與資料（Step 4~6，子 agent 執行）

> [!CAUTION]
> **Step 2、Step 4~11 都必須將任務委派給子 agent。**

#### 並行派發 ①：Step 4 + Step 6（fields_refreshed 後觸發）

Step 6（示例資料）僅依賴 `worksheetContext.json` 和 `worksheetIdByName`（Step 3 的產出），與 Step 4/5 無資料依賴。因此：
- Step 3 完成後，同時派發 Step 4 和 Step 6
- Step 4 → Step 5 序列推進，**不等待 Step 6**
- Step 6 作為後臺任務執行，在 Step 5 完成前確認完成即可

Step 5 和 Step 6 都完成後，排程器寫入 `progress=sample_data_created`。

---

### 階段 2.5：頁面空殼建立（Step 5b，內聯執行）

Step 5b 是輕量操作（建立空白頁面導航項 + chatbot），為後續三路並行提供 ID 依賴。

讀取 `build/steps/5b_create_page_shells.md` → 執行 → 排程器寫入 `progress=page_shells_created`

---

### 階段 3：配置並行（Step 7 + Step 8 + Step 9，子 agent 執行）

#### 並行派發 ②：Step 7 + Step 8 + Step 9（page_shells_created 後觸發）

Step 5b 完成後，三者的輸入已全部就緒：
- **Step 7**（配置頁面元件）：需要 `customPageIdByName`（Step 5b）+ `worksheetContext` + `viewIdByName`
- **Step 8**（建立角色）：需要 `customPageIdByName` + `chatbotIdByName`（Step 5b）+ `worksheetContext` + `viewIdByName`
- **Step 9**（設計工作流）：需要 `worksheetContext` + `viewIdByName` + `roles[]`（來自 hap-plan.json，不依賴 roleContext）

因此：
- Step 5b 完成後，同時派發 Step 7、Step 8、Step 9
- 三者都完成後，排程器寫入 `progress=config_completed`

---

### 階段 4：工作流部署（Step 10 + Step 11，子 agent 執行）

#### 並行派發 ③：Step 10 + Step 11（config_completed 後觸發）

Step 10（系統工作流）和 Step 11（自訂動作工作流）均依賴 Step 9 的設計產出，彼此無依賴。因此：
- `config_completed` 後，同時派發 Step 10 和 Step 11
- 兩者都完成後，排程器寫入 `progress="workflows_deployed"`

---

### 階段 5：CLI 建後精修（Step 12，內聯執行）

Step 12 用 `hap` 命令列工具補 MCP 蓋不到的硬缺口。**永不阻斷**：CLI 不可用/組織不一致時降級為
「待補清單」，應用仍算搭建成功。

讀取 `build/steps/12_cli_refinement.md` → 內聯執行 → 排程器寫入 `progress="completed"`。

> 本步內聯執行（非 subagent）：它依賴構建入口「CLI 自檢」寫入的 `cliAvailable`，
> 且以對賬+少量 CLI 命令為主，上下文開銷小。

---

### 子 agent 執行流程

對 Step 4~11 的每一步：

1. **必須將任務委派給子 agent**，使用下方 Prompt 模板
2. **委派成功** → 等待子 agent 完成 → 驗證產出資料是否到位（對照全域性執行清單）→ 排程器寫入 progress
3. **子 agent 不可用** → 退回內聯：完整讀取步驟檔案，在主 agent 內執行

#### 子 agent Prompt 模板

```
你是 HAP 应用搭建执行器，负责执行一个特定的搭建步骤。

## 你的任务
完整阅读步骤文件 `{STEP_FILE_PATH}` 并严格按其要求执行。

## 关键信息
- 应用名称：{appName}
- 项目根目录：{PROJECT_ROOT}
- Skill 目录：{SKILL_DIR}（步骤文件所在的 skill 根目录）
- 方案文件：{PROJECT_ROOT}/apps/{appName}/hap-plan.json
- 进度文件：{PROJECT_ROOT}/apps/{appName}/hap-context.json
- 字段结构：{PROJECT_ROOT}/apps/{appName}/worksheetContext.json（如存在）
- 引用的规则文件：{RULE_FILES}（如果步骤文件引用了共享规则文件，此处填入路径列表；没有则留空）

## 执行要求
1. 先完整读取步骤文件
2. **如果步骤文件引用了其他规则文件（如 `workflow_rules.md`），必须先完整阅读该规则文件后再开始执行**
3. 从 hap-plan.json 读取方案数据
4. 从 hap-context.json 读取已有的 ID 映射
5. 如需字段信息，从 worksheetContext.json 读取（只读）
6. 如步骤文件要求运行脚本（如 generate_fill_templates.py），使用 `{SKILL_DIR}` 定位脚本路径
7. 严格按步骤文件中的规则执行所有操作
8. 所有 MCP 调用必须使用调度器指定的明道云 MCP 服务（服务名称由调度器在委派时传入）
9. 完成后严格按步骤文件中「完成标志」章节的要求写入数据。写入目标可能是 `hap-context.json` 或 `hap-plan.json`，以步骤文件为准。不写 `progress`（由调度器统一管理）
10. 验证步骤文件末尾的 ⛔ 验证断言全部通过
11. 输出**执行问题总结**：列出执行过程中遇到的所有问题（如 API 报错、字段/选项映射失败、节点跳过、重试等），每条包含问题描述和处理方式。如果全程无问题，输出「无异常」
```

---

### 驗證與播報（每步通用）

每步完成後：

1. 驗證該步驟的交付物欄位非空（對照全域性執行清單）
2. 驗證透過後，**由排程器寫入對應的 `progress` 值**到 `hap-context.json`
3. 若驗證失敗 → 向使用者報告錯誤並停止

**Step 9 特殊驗證（排程器必須執行）**：

Step 9 的產出是寫入 `hap-plan.json` 而非 `hap-context.json`。排程器必須在子 agent 完成後：

1. 重新讀取 `hap-plan.json`，檢查每條 `workflows[]` 和 `customActionWorkflows[]` 的 `nodes` 陣列是否非空且長度 ≥ 1
2. 檢查失敗 → **不寫入 progress**，向使用者報告哪些工作流缺少節點方案，並重新派發 Step 9

**播報節點**（非播報節點靜默）：

| 時機 | 輸出模板 |
|------|---------| 
| 搭建開始 | `🚀 开始搭建应用【{appName}】…` |
| 階段 1 完成 | `✅ 基础搭建完成：应用已创建，{N} 张工作表` |
| Step 5b 完成 | `✅ 页面空壳与 AI 助手已创建，开始并行配置…` |
| 階段 3 完成 | `✅ 页面组件、角色、工作流设计全部完成` |
| 階段 4 完成 | `✅ 工作流已全部发布，开始建后精修…` |
| Step 12 完成（已回填） | `✅ 建后精修完成：已用 CLI 补齐 {N} 项 MCP 未覆盖的配置` |
| Step 12 完成（降級，hap 未安裝） | `ℹ️ 应用已建好；安装并登录 hap-cli 后可补齐 {M} 项增强配置（见摘要）` |
| 全部完成 | 輸出完整摘要（見下方「完成」章節） |

---

## 路由表

| progress 值 | 下一步 | 步驟檔案 | 執行方式 | 引用規則檔案 |
|---|---|---|:---:|---|
| （無/新建） | Step 1：建立應用與導航 | `build/steps/1_create_app.md` | 🔵 內聯 | — |
| `app_created` | Step 2：建立工作表 | `build/steps/2_create_worksheets.md` | 🟢 subagent | — |
| `worksheets_created` | Step 3：重新整理欄位結構 | `build/steps/3_refresh_fields.md` | 🔵 內聯 | — |
| `fields_refreshed` | Step 4 + **⚡ Step 6**：並行派發 | `4_create_actions.md` + `6_create_sample_data.md` | 🟢 subagent | — |
| `actions_created` | Step 5：建立檢視 | `build/steps/5_create_views.md` | 🟢 subagent | — |
| `sample_data_created` | Step 5b：建立頁面空殼與 AI 助手 | `build/steps/5b_create_page_shells.md` | 🔵 內聯 | — |
| `page_shells_created` | **⚡ 三路並行** Step 7 + Step 8 + Step 9 | `7_create_pages.md` + `8_create_roles.md` + `9_design_workflows.md` | 🟢 subagent | Step 9 無引用 |
| `config_completed` | **⚡ 並行派發** Step 10 + Step 11 | `10_create_workflows.md` + `11_create_action_workflows.md` | 🟢 subagent | `build/steps/workflow_rules.md` |
| `workflows_deployed` | Step 12：CLI 建後精修對賬與回填 | `build/steps/12_cli_refinement.md` | 🔵 內聯 | `build/CAPABILITY_MATRIX.md` |

---

## 完成

在標記 `progress="completed"` 之前，**必須回到頂部的「🔒 全域性執行清單」逐項核對**。並行派發的步驟須等待全部完成後再推進（詳見上方「並行派發策略」）。

確認全部 15 項均已完成後，輸出成功摘要：

- 應用名稱和連結
- 已建立的工作表數量
- 已寫入的示例資料記錄條數
- 已建立併發布的工作流數量（系統工作流 + 自訂動作工作流）
- 已建立的角色數量
- 已建立的 AI 助手數量（若有）
- CLI 建後精修結果：已回填 N 項 /（或）待補清單 M 項（CLI 未安裝或組織不一致時）

---

## 禁止事項

- **禁止跳過 step 檔案**直接憑經驗執行
- **禁止偽造 ID**——appId、worksheetId、fieldId、viewId、workflowId 必須來自工具返回值
- **禁止把 MCP 原始返回全文寫入 context**——只提取關鍵 ID 和對映
- **禁止一個 step 修改其他 step 的職責範圍**
- **禁止跳步**——必須嚴格按路由表順序執行

## 輸出格式

- 使用加粗和反引號標註關鍵名稱和數字
- 不使用其他 Markdown 格式
- 錯誤示例：`❌ Step 2 创建工作表失败：【任务清单】未能创建，原因：xxx`
