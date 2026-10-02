# Step 12：建後精修（CLI 對賬與回填）

你是 niio 應用建置的**收尾精修執行器**。MCP 已經把應用從零建好，但 MCP 的工具是「建立導向」的，
有少數設定項 MCP 表達不出來（如檢視的部分增強設定、角色對 AI 助手的訪問權等）。本步用 `hap`
命令列工具（CLI）把這些 **MCP 蓋不到的硬缺口**補上。

> [!IMPORTANT]
> 本步**只補硬缺口**——即「MCP 完全做不到」的項。MCP 能做的物件一律不碰，避免同一物件被
> MCP + CLI 雙寫產生衝突。硬缺口的判定依據是 `build/CAPABILITY_MATRIX.md` 的「CLI-only 硬缺口」列。

> [!CAUTION]
> 本步**永不讓建置失敗**。CLI 不可用或與應用不同組織時，跳過回填、輸出「待補清單」即可，
> 應用本身已由 MCP 建好，仍算建置成功。

## 輸入資料

- `appId`、`org_id`、各 ID 對映：來自 `hap-context.json`
- `cliAvailable`：來自 `hap-context.json`（建置入口的「CLI 自檢」寫入）
- `worksheetContext.json`：真實欄位/檢視結構（只讀）
- `hap-plan.json`：方案期望（檢視增強設定、角色權限、動作觸發條件、節點設計等）
- `build/CAPABILITY_MATRIX.md`：硬缺口清單與各物件的「Step 12 檢查點」

## 執行流程

### 步驟 0：確保 CLI 就緒（組織校正 + 設為當前應用）

讀 `cliAvailable`：

- **`cliAvailable = false`**（hap 未安裝，或已安裝但瀏覽器授權始終未完成）→ 跳到
  「步驟 3：降級輸出」。這是**唯一**跳過回填的情形。
- **`cliAvailable = true`** → 做以下「就緒校正」，然後進入步驟 1：

  1. **組織一致性**：執行 `hap auth whoami` 讀當前組織，與 `hap-context.json` 的 `org_id` 比對。
     - 不一致 → 執行 `hap auth set-current-org <org_id>` **自動切換**到本應用所在組織。
       （不要讓使用者手動切換。）
  2. **設為當前應用**：執行 `hap app select <appId>`，把正在建置的應用設為預設應用。
     - `set-current-org` 會清空預設應用，所以切組織後**必須**重新 `app select`；
       即使組織本就一致也執行此步，使後續回填命令無需反覆傳 `--app-id`。

### 步驟 1：對賬，得出 `cliGaps[]`

> 不依賴任何「各 step 邊建邊記」的資料——本步在最後**統一對賬**重新算出硬缺口。

逐項對照 `build/CAPABILITY_MATRIX.md` 每個物件的「Step 12 檢查點」，用 CLI 讀出真實結構、與
`hap-plan.json` 期望比對，把「MCP 沒做到、且屬於 CLI-only 硬缺口」的項收整合執行期清單 `cliGaps[]`。

對賬時優先核對硬缺口清單裡的高頻項（按矩陣排序）：

1. **檢視增強設定**：plan 期望的 color / group / filterList / 封面 / quickActions 等，
   逐檢視用 `hap --json worksheet view info <ws_id> <view_id>` 讀現狀，缺的記入 `cliGaps`。
2. **角色 → AI 助手訪問權**：plan 中角色應能訪問的 AI 助手 vs 角色實際權限（已知歷史缺口，必查）。
3. **角色細粒度權限/成員**。
4. **工作流節點深設定**：plan 節點設計意圖 vs 實建節點設定。
5. **動作按鈕高階設定**（觸發條件/可見性）。
6. **特殊欄位型別**（`create_worksheet` 不支援、被降級或缺失的欄位）。
7. **頁面元件細設定**。

每條 `cliGaps[]` 記錄：`{ object, id, op, intent, evidence }`
（物件型別、目標 id、要執行的 CLI 操作、方案意圖、對賬證據=期望 vs 現狀）。

> `cliGaps` 為空 → 說明 MCP 已全部覆蓋，直接進入「完成」。

### 步驟 2：逐項回填

對每條 `cliGaps[]`，呼叫對應 `hap` 命令回填。命令寫法**直接複用 app 編輯能力的命令字典**
（檢視 / 工作流節點 / 角色 / 頁面元件 / 欄位 / 動作各模組），本步只做橋接，不自創編輯邏輯：

- 各種 id 從 `hap-context.json` 取（appId、worksheetId、viewId、roleId、processId/nodeId…）；
  這些是同後端的伺服器端 id，CLI 直接可用。
- 改複雜值前**先用讀命令匯出現狀**，在真實結構上改再寫回（檢視/節點/頁面這類整體寫回的物件尤其如此）。
- **逐條記錄結果**：成功 / 失敗（含原因）。單條失敗不影響其他項，繼續。

> [!CAUTION]
> 回填只針對 `cliGaps[]` 列出的硬缺口。**不要**用 CLI 去重做 MCP 已經建好的物件。

### 步驟 3：降級輸出（僅 `cliAvailable = false`，即 hap 未安裝/未完成登入）

不回填，改為把按 plan 推斷的待補項渲染成**「待補清單」**寫入收尾摘要：

> ℹ️ 應用已建好。以下增強設定 MCP 暫未覆蓋。安裝並登入 hap-cli 後，可用「應用編輯」能力補齊：{清單}
>
> 安裝：`pip install hap-cli`；登入：`hap auth login`（瀏覽器授權）。

清單每項寫明：物件、所在工作表/頁面、要補什麼（自然語言），不要寫裸命令。

> 組織不一致**不再**走降級——CLI 可用時已在步驟 0 自動切換組織並設當前應用。

## 完成

不寫 `progress`（由排程器統一管理）。排程器在本步透過後寫入 `progress="completed"`。

**⛔ 驗證斷言**：
1. 已讀取 `cliAvailable` 並據此分流；
2. `cliAvailable = true` 時：步驟 0 已完成組織校正（必要時 `set-current-org`）+ `app select <appId>`；
   `cliGaps[]` 已對賬得出，且每條已嘗試回填並記錄結果（成功/失敗）；
3. `cliAvailable = false` 時：已輸出「待補清單」（含安裝/登入指引），**未中斷建置**；
4. 本步從未因 CLI 相關問題讓整體建置判為失敗。

## 輸出要求

- 簡潔彙報：本步補了幾項、失敗幾項（附原因）、或降級為待補清單（附清單條數）。
- 失敗項與待補項都要讓使用者能據此手動跟進（後續用「應用編輯」能力自行補）。

## 邊界

- 本步**只做 `cliGaps[]` 的回填**，到此為止。
- **開放式精修 / 進一步改動不代勞**：收尾引導使用者後續用 `hap` 命令列的「應用編輯」能力
  （從讀取應用結構起步）自行修改，本步不主動擴大改動範圍。
