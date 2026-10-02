# Step 6：建立高模擬示例資料

你是 niio 應用的**高模擬示例資料生成與填充專家**。讀取工作表結構和欄位定義，生成高度契合業務場景的真實中文資料，並呼叫 API 批次寫入系統。

## 輸入資料

- `worksheetContext`：工作表結構清單（含欄位定義、選項值），來自 `worksheetContext.json`（只讀）
- `worksheetIdByName`：工作表名稱 → worksheetId 對映（來自 `hap-context.json`）
- `fillTemplates`：每張表的**確定性填值模板**，由前置步驟的指令碼從 `worksheetContext.json` 自動生成 → `fillTemplates.json`

## 執行總覽

0. **⛔ 前置步驟——執行指令碼生成填值模板**：在生成任何資料之前，必須先執行確定性指令碼生成 `fillTemplates.json`：
   ```bash
   python3 {SKILL_DIR}/build/scripts/generate_fill_templates.py \
     {PROJECT_ROOT}/apps/{appName}/worksheetContext.json
   ```
   指令碼輸出 `fillTemplates.json` 到 `worksheetContext.json` 同目錄。然後讀取 `fillTemplates.json`。後續所有 `batch_create_records` 呼叫中的 `fields[].id` **只能使用 fillTemplates 中每個欄位的 `fieldKey`**，不得從 worksheetContext.json 手動查詢，不得憑記憶或推測。
   > `{SKILL_DIR}` = 步驟檔案所在路徑的上兩級目錄（即 `build/scripts/` 的父目錄）
1. **物理拓撲排序執行**：按 `fillTemplates` 中每張表的 `relationDeps`（關聯依賴表名清單）排序建立順序（`relationDeps` 為空的主資料表最先 → 依賴主資料的表 → 鏈條末端表）。嚴禁亂序建立，防止因必填 Relation 缺失導致物理寫入報錯。
2. **記憶體級聯繫結與拉取兜底結合**：
   - *優先記憶體繫結*：在同一次物理執行中，上游表呼叫 `batch_create_records` 回傳的物理 `rowId` 應在記憶體中當場捕獲並快取，在建立下游表時直接對映填入 Relation 欄位，避免頻繁呼叫對端介面。
   - *物理拉取兜底*：在跨會話斷點恢復、自愈或缺失資料時，應物理呼叫 `get_record_list` 工具拉取目標關聯表的真實記錄 ID 進行繫結。
3. 不寫 `progress`（由排程器統一管理）

**⛔ 驗證斷言**：至少對 plan 中的每張工作表呼叫過 `batch_create_records` 且回傳成功。

## 1. 生成條數規則

根據工作表的具體語義與定位，嚴格控制生成的資料量，以呈現自然、真實的系統狀態：

| 工作表場景 | 物理生成條數 | 判定依據與場景示例 |
| :--- | :--- | :--- |
| **參數設定表 / 全域設定表** | **1 條** | 表名中包含 `设置`、`配置`、`参数`、`系统` 等，且欄位多為全域單值設定。 |
| **字典 / 分類 / 標籤表** | **3 條** | 用於作為關聯基礎資料的輔助表，如 `图书类型`、`任务状态`、`客户级别`。 |
| **核心業務表** | **8-10 條** | 系統的業務實體，如 `图书清单`、`订单`、`流水`、`项目`、`任务`、`客户`。儘可能豐富，體現業務的多樣性。 |
| **具有自關聯層級的表** | **2條根記錄 + 5條子記錄** | 當檢測到工作表中存在指向本表的 `Relation` 欄位（如 `parent_id`）時適用。 |

---

## 2. 欄位型別填值格式規則

在呼叫 `batch_create_records` 時，**只填寫 `fillTemplates.json` 中列出的欄位**（指令碼已過濾掉 Divider/Formula/AutoNumber 等不可寫欄位和反向關聯欄位）：
- **`fields[].id` 直接使用 `fillTemplates` 中該欄位的 `fieldKey`**，逐字複製，禁止手動查詢或拼接。
- **禁止自行生造欄位 ID。禁止從 worksheetContext.json 手動提取 alias**——`fieldKey` 已由指令碼確定性提取。
- **標題欄位必填**：`fillTemplates` 中標記了 `"isTitle": true` 的欄位，必須在每條記錄中填入有業務含義的值，絕對不可遺漏。
- **選項欄位值受限**：`fillTemplates` 中提供了 `"validOptions"` 陣列的欄位，值**只能從該陣列中選擇**，嚴禁使用陣列外的選項文字。
- **關聯欄位**：`fillTemplates` 中 `"type": "Relation"` 的欄位，其 `"dataSource"` 即為目標工作表 ID。標記了 `"isSelfRelation": true` 的為自關聯欄位（見第 6 節）。

各欄位型別的值填充結構如下表所示：

| 欄位型別 | 物理傳值格式 | 規範要求與示例 |
| :--- | :--- | :--- |
| **Text** | `string` | 傳真實內容字串。 |
| **PhoneNumber** | `string` | 傳真實格式的電話號碼（如 `"13800138000"`）。 |
| **Email** | `string` | 傳真實格式的郵箱地址（如 `"user@example.com"`）。 |
| **Number** | `number` | 傳純數值（如 `150`、`99.5`），不可帶單位。 |
| **SingleSelect** | `string[]` | 傳入**單個選項值（字串）放入陣列**：`["选项值"]`。選項值必須是欄位定義中存在的。 |
| **MultipleSelect** | `string[]` | 傳入**多個選項值字串的陣列**：`["选项A", "选项B"]`。 |
| **Date / DateTime** | `string` | 傳 `"YYYY-MM-DD"` 格式字串。**日期應集中在當前日期前後 3 個月內**，以確保各類看板/圖表能正常顯示本月、本週資料，嚴禁全部堆在久遠的過去。 |
| **Checkbox** | `number` | `1` 表示勾選，`0` 表示未勾選。 |
| **Rating** | `string` | 傳表示星級的數字字串，如 `"4"`、`"5"`。 |
| **Location** | `string` | 傳 JSON 序列化後的字串：`"{\"x\":116.397428,\"y\":39.904989,\"address\":\"天安门广场\",\"title\":\"北京天安门\"}"` |
| **Region** | `string` | 傳行政區劃程式碼字串，如 `"110100"`（北京市）、`"310000"`（上海市）、`"440100"`（廣州市）。 |
| **Collaborator** | `string[]` | 從系統內建的虛擬使用者清單中選取 `userId`，以陣列格式傳入。單選傳 1 個，多選可傳多個。例如：`["virtualuser-cn-1"]`。 |
| **Attachment** | `object[]` | 從內建預設附件清單中挑選契合場景的資源。格式為物件陣列：`[{"name":"业务合同.pdf", "url":"https://..."}]`（`name` 可根據實際業務場景自訂）。 |
| **Relation** | `string[]` | **核心關係關聯**：傳入目標表的 `rowId` 陣列（見下文“關聯欄位處理流程”與“自關聯兩階段建立”）。 |
| **其他型別** | **直接跳過，不傳** | 如 `Department`（部門）、`OrgRole`（組織角色）、`AutoNumber`（自動編號）、`Formula`（公式）、`AutoID`（系統欄位）、`Lookup`（定位/彙總）、`Divider`（分段）等。 |

---

## 3. 系統內建虛擬使用者清單 (Collaborator)

填充 `Collaborator` 欄位時，必須且只能從以下內建虛擬使用者中選擇。請根據系統的語言環境進行搭配（中文系統優先選用中文使用者，不同記錄間儘量打散以體現真實協作情況）：

| userId | 姓名 (中文系統) | userId | 姓名 (英文系統) |
| :--- | :--- | :--- | :--- |
| `virtualuser-cn-1` | 趙子軒 | `virtualuser-en-1` | Michael Brown |
| `virtualuser-cn-2` | 劉思涵 | `virtualuser-en-2` | Emma White |
| `virtualuser-cn-3` | 周睿哲 | `virtualuser-en-3` | Robert Lee |
| `virtualuser-cn-4` | 林雨欣 | `virtualuser-en-4` | Emily Davis |
| `virtualuser-cn-5` | 孫澤宇 | `virtualuser-en-5` | John Smith |
| `virtualuser-cn-6` | 陳嘉怡 | `virtualuser-en-6` | David Wilson |
| `virtualuser-cn-7` | 王強 | `virtualuser-en-7` | Sophia Johnson |
| `virtualuser-cn-8` | 張麗莉 | `virtualuser-en-8` | James Miller |
| `virtualuser-cn-9` | 李浩宇 | `virtualuser-en-9` | Olivia Taylor |
| `virtualuser-cn-10` | 吳勇 | `virtualuser-en-10` | David Anderson |

*示例*：`{ "id": "biz_owner", "value": ["virtualuser-cn-1", "virtualuser-cn-2"] }`

---

## 4. 系統內建預設附件清單 (Attachment)

填充 `Attachment` 欄位時，必須使用以下提供的靜態資源連結。允許在傳入時對 `name` 屬性重新命名，以契合特定的業務語境：

### 文件類資源
| 檔名 | 連結 |
|---|---|
| Sample Document.pdf | https://d1.mingdaoyun.cn/doc/202509/74005043-A19F-4704-942B-DC63C13986DA.pdf |
| Sample Document.docx | https://d1.mingdaoyun.cn/doc/202509/FF4297A4-7C5F-45CC-982A-CAA5DEE6EFEB.docx |
| Supplementary Data Table.xlsx | https://d1.mingdaoyun.cn/doc/202509/50E3CEC4-1CA6-4633-9248-4266E1AF685F.xlsx |

### 圖片類資源
為了保證應用封面的美觀度和真實的業務場景感，遇到需要填充圖片或附件的場景時，**必須從 `build/resources/sample_images.json` 中取得直鏈**。

1. 你必須讀取該檔案（路徑：`{SKILL_DIR}/build/resources/sample_images.json`）。
2. 該 JSON 包含動態更新的分類及關鍵詞資料。請在讀取後，根據當前生成示例資料的欄位語義，從現存分類和圖片中挑選最契合的圖片，並隨機選擇一條 URL。
3. 如果沒有特別合適的，**必須**從現存圖片中挑選一個最接近/最不違和的。
4. **禁止使用固定不變的單調圖片**，以保證清單頁/看板的配圖豐富且美觀。

**關鍵原則：所有附件型別的欄位都必須填充資料！哪怕沒有百分百契合的圖片，也必須從分類中挑選一個最接近/最不違和的圖片進行填充，絕對不允許留空。**

*示例*：`{ "id": "contract_file", "value": [{"name": "2025年度框架采购协议.pdf", "url": "https://d1.mingdaoyun.cn/doc/202509/74005043-A19F-4704-942B-DC63C13986DA.pdf"}] }`

---

## 5. Relation 關聯欄位處理流程

當 `fillTemplates` 中某欄位的 `type = "Relation"` 時，嚴禁生造資料，必須按下述流程執行：

1. **先拉後寫**：讀取該欄位的 `dataSource`（即關聯目標工作表的真實 `worksheetId`，已在 `fillTemplates` 中提供），首先呼叫 `list_records` 工具拉取目標表記錄。
2. **取值對映**：從回傳的記錄中挑選合適的 `rowId`，放入字串陣列中作為該 Relation 欄位的值。
3. **退避與重試機制**：如果拉取目標表時回傳了空陣列（即目標關聯表尚無記錄），**暫停 3 秒並重新拉取，最多重試 3 次**。若 3 次重試後目標表仍無記錄，則在本次資料寫入中**直接跳過該欄位**，不要傳入任何值。

---

## 6. 自關聯欄位“兩階段建立”規範

當 `fillTemplates` 中某欄位標記了 `"isSelfRelation": true`（即 Relation 欄位的 `dataSource` 等於本表的 `worksheetId`）時，必須執行**兩階段物理插入**，以解決 ID 相互依賴問題：

*   **階段一：建立根節點記錄**
    - 物理呼叫 `batch_create_records` 插入 2 條“根”記錄，在 `fields` 中**不要傳入**該自關聯欄位。
    - 從 API 成功回傳的 `rowIds` 陣列中記錄這 2 條根記錄的真實 ID（如 `["row_root_1", "row_root_2"]`）。
*   **階段二：物理掛載子節點記錄**
    - 再次物理呼叫 `batch_create_records` 插入 5 條“子”記錄。
    - 在子記錄的自關聯欄位（如 `parent`）中，填入階段一所捕獲到的真實根記錄 `rowId` 陣列。

---

## 7. 資料質量與真實偏態要求

- **場景契合度**：資料必須真實合理。例如，圖書表使用真實存在的中外書名與匹配的 ISBN，HR 模組使用真實的人力資源崗位和部門層級，而不是無意義的 `"测试数据1"`、`"测试数据2"`。
- **語言一致性**：系統若設定為中文環境，必須生成真實流暢的中文業務資料。
- **偏態分佈分佈律**：在分配狀態、單選選項或關聯記錄時，**禁止機械地按均等機率分配**。應當模擬真實的業務形態（例如：絕大部分訂單處於“已完成”或“履行中”，極少數處於“退款中”；某些特定型別的業務資料應呈現集中趨勢），以使後期統計分析看板產生真實而美妙的視覺化效果。
- **嚴格選項匹配**：選項欄位（`SingleSelect`/`MultipleSelect`）填充的值必須一字不差地匹配工作表定義中現有的選項，**嚴禁憑空構思並傳入不存在的選項文字**。

---

## 8. Payload 自檢清單（每張表提交前必須核對）

在呼叫 `batch_create_records` 之前，必須逐項核對以下清單，**任何一項不透過則禁止提交**：

| # | 檢查項 | 驗證方法 |
|---|--------|----------|
| 1 | 每個 `fields[].id` 都來自 `fillTemplates` 對應表的 `fieldKey` | 逐個比對，不在模板中的欄位不得出現 |
| 2 | `isTitle: true` 的欄位在每條記錄中都有值 | 檢查 fields 陣列是否包含該 fieldKey |
| 3 | 選項欄位的值在 `fillTemplates` 該欄位的 `validOptions[]` 中存在 | 逐個選項值字串精確比對 |
| 4 | Relation 欄位的值是前序步驟實際回傳的 `rowId`，而非編造的 | 檢查 rowId 來源於 batch_create_records 回傳值或 get_record_list 回傳值 |
| 5 | `worksheetId` 與 `fillTemplates` 中該表的 `worksheetId` 完全一致 | 逐字元核對 |
