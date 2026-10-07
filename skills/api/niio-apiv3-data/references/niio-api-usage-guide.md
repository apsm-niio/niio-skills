> **部署設定**：範例 API 使用 `https://niiodemo.apsm.com.tw`；其他部署須替換為該環境網址與憑證。API、MCP 與網站網址必須使用本次選定部署環境的已確認設定，三者可能不同，不得只依 MCP 網址推測 API 或網站位置。範例網域不代表 REST 路由已驗證；MCP 成功也不代表 REST 或 CLI 相容。使用 REST 功能前，須依部署文件確認路徑與驗證方式，先完成唯讀測試；404 HTML 時停止，不重試寫入。下方 `.example.invalid` 網址只是不可連線的佔位範例，執行前必須替換；未確認網址時先詢問，不得向佔位網址傳送憑證。圖片與附件只能使用使用者提供或已授權的素材網址。

# niio V3 API 使用規範完整指南

> 本文件總結了niio V3 API的核心使用規範、最佳實踐和常見陷阱,基於實際測試驗證

## 📚 如何取得最新的 API V3 文件

在開始使用 niio API V3 之前,建議先透過以下方式取得最新的 API 文件:

### 方式一: 使用應用 API MCP 伺服器 (推薦)

透過 MCP 伺服器直接訪問最新的 API V3 文件結構。當你看到以下 JSON 代表是 官方API文件的 MCP設定


**設定方法**:

```json
{
  "mcpServers": {
    "應用 API - API 文件": {
      "command": "npx",
      "args": [
        "-y",
        "apifox-mcp-server@latest",
        "--site-id=5442569"
      ]
    }
  }
}
```

**💡 關於其他 MCP 設定**: 如需設定 niio 應用 MCP (用於操作 niio 資料),請參考 niio MCP 使用指南

---

### 方式二: 訪問線上文件

如果無法透過 MCP訪問到應用 API文件,可以透過以下線上地址直接訪問 API V3 文件:

**概述文件**:
- API 整體介紹（請參閱此技能隨附文件或部署管理者提供的說明）
- 欄位型別對照表（請參閱此技能隨附文件或部署管理者提供的說明）
- 篩選器使用指南（請參閱此技能隨附文件或部署管理者提供的說明）
- 錯誤碼說明（請參閱此技能隨附文件或部署管理者提供的說明）

**API 端點文件**: 完整的 API 端點清單見文件後面的"線上文件資源"章節。

---

## 線上文件資源

優先使用 MCP 伺服器訪問最新的 API 文件結構。如果 MCP 不可用,可以透過以下官方線上文件取得。

### 應用 API V3 文件

#### 概述文件
- V3-beta (AI 友好) 概述（請參閱此技能隨附文件或部署管理者提供的說明） - API 整體介紹和使用說明
- V3-beta (AI 友好) 欄位型別對照表（請參閱此技能隨附文件或部署管理者提供的說明） - 完整的欄位型別說明
- V3-beta (AI 友好) 篩選器使用指南（請參閱此技能隨附文件或部署管理者提供的說明） - Filter 物件詳細說明
- V3-beta (AI 友好) 錯誤碼（請參閱此技能隨附文件或部署管理者提供的說明） - API 錯誤碼說明

#### 應用 API 端點文件
- **應用**: 取得應用資訊（請參閱此技能隨附文件或部署管理者提供的說明）
- **工作表**:
  - 取得工作表清單（請參閱此技能隨附文件或部署管理者提供的說明）
  - 取得工作表結構資訊（請參閱此技能隨附文件或部署管理者提供的說明）
  - 編輯工作表（請參閱此技能隨附文件或部署管理者提供的說明）
  - 刪除工作表（請參閱此技能隨附文件或部署管理者提供的說明）
  - 新建工作表（請參閱此技能隨附文件或部署管理者提供的說明）
- **工作表行記錄**:
  - 取得行記錄清單（請參閱此技能隨附文件或部署管理者提供的說明）
  - 取得行記錄詳情（請參閱此技能隨附文件或部署管理者提供的說明）
  - 新建行記錄（請參閱此技能隨附文件或部署管理者提供的說明）
  - 更新行記錄（請參閱此技能隨附文件或部署管理者提供的說明）
  - 刪除行記錄（請參閱此技能隨附文件或部署管理者提供的說明）
  - 批次新增行記錄（請參閱此技能隨附文件或部署管理者提供的說明）
  - 批次更新行記錄（請參閱此技能隨附文件或部署管理者提供的說明）
  - 批次刪除行記錄（請參閱此技能隨附文件或部署管理者提供的說明）
  - 取得關聯記錄（請參閱此技能隨附文件或部署管理者提供的說明）
  - 取得行記錄透視資料（請參閱此技能隨附文件或部署管理者提供的說明）
  - 取得記錄分享連結（請參閱此技能隨附文件或部署管理者提供的說明）
  - 取得行記錄日誌（請參閱此技能隨附文件或部署管理者提供的說明）
  - 取得行記錄討論（請參閱此技能隨附文件或部署管理者提供的說明）
- **選項集**:
  - 取得選項集清單（請參閱此技能隨附文件或部署管理者提供的說明）
  - 建立選項集（請參閱此技能隨附文件或部署管理者提供的說明）
  - 編輯選項集（請參閱此技能隨附文件或部署管理者提供的說明）
  - 停用選項集（請參閱此技能隨附文件或部署管理者提供的說明）
- **工作流**:
  - 取得流程清單（請參閱此技能隨附文件或部署管理者提供的說明）
  - 取得流程詳情（請參閱此技能隨附文件或部署管理者提供的說明）
  - 觸發流程（請參閱此技能隨附文件或部署管理者提供的說明）
- **角色**:
  - 取得角色清單（請參閱此技能隨附文件或部署管理者提供的說明）
  - 建立角色（請參閱此技能隨附文件或部署管理者提供的說明）
  - 取得角色詳情（請參閱此技能隨附文件或部署管理者提供的說明）
  - 刪除角色（請參閱此技能隨附文件或部署管理者提供的說明）
  - 新增角色成員（請參閱此技能隨附文件或部署管理者提供的說明）
  - 移除角色成員（請參閱此技能隨附文件或部署管理者提供的說明）
  - 成員退出所有角色（請參閱此技能隨附文件或部署管理者提供的說明）
- **公共查詢**:
  - 查詢成員（請參閱此技能隨附文件或部署管理者提供的說明）
  - 查詢部門（請參閱此技能隨附文件或部署管理者提供的說明）
  - 取得地區資訊（請參閱此技能隨附文件或部署管理者提供的說明）

### 使用建議

1. **優先使用 MCP**: 透過設定好的 MCP 伺服器可以直接在 Claude Code 中訪問最新的 API 結構,無需手動查閱文件
2. **線上文件作為補充**: 當需要詳細說明或示例時,可以訪問上述線上文件
3. **關注欄位型別**: 欄位型別對照表和篩選器使用指南是最常用的參考文件
4. **錯誤排查**: 遇到 API 呼叫問題時,先檢視錯誤碼文件

---

## 目錄

0. [快速開始 - API 使用流程](#零快速開始---api-使用流程)
1. [建立工作表規範](#一建立工作表規範)
2. [欄位型別參數詳解](#二欄位型別參數詳解)
3. [建立/更新記錄規範](#三建立更新記錄規範)
4. [查詢篩選規範](#四查詢篩選規範)
5. [資料透視分析規範](#五資料透視分析規範)
6. [關聯欄位完整指南](#六關聯欄位完整指南)
7. [常見陷阱與解決方案](#七常見陷阱與解決方案)

---

## 零、快速開始 - API 使用流程

### 0.1 niio V3 API 整體架構

```
niio組織
  └── 應用 (Application)
       ├── 角色 (Role)
       ├── 工作流 (Workflow)
       ├── 工作表分組 (Section)
       └── 工作表 (Worksheet)
            ├── 欄位 (Field/Control)
            ├── 檢視 (View)
            └── 記錄 (Row/Record)
```

---

### 0.2 從零建置應用的完整流程

#### **階段一: 準備工作**

**Step 1: 取得 API 憑證**

身分驗證與授權憑證統一放在請求 **Header** 中，每個請求都必須攜帶。V3 支援三種身分驗證與授權方式：

| 方式 | Header 參數 | 建立者 | 操作身份 | 有效期 | 適用場景 |
| --- | --- | --- | --- | --- | --- |
| **AppKey + Sign** | `HAP-Appkey`、`HAP-Sign` | 管理員 | 應用管理員 | 長期 | 伺服器端整合 |
| **PAT** | `Authorization: Bearer {access_token}`、`HAP-Appid`（部分介面必填） | 個人 | 個人 | 可設定 | 個人指令碼 / 工具 |
| **OAuth 2.0** | `Authorization: Bearer {access_token}`、`HAP-Appid`（部分介面必填） | 整合開發者 | 被授權使用者 | 短期，自動重新整理 | 第三方應用整合 |

- **AppKey + Sign**：應用金鑰身分驗證與授權，由管理員在「應用 → 設定 → API 金鑰」建立，以應用管理員身份訪問資料。需要取得 **AppKey**、**Sign**、**應用 ID (app_id)**。
- **PAT**：個人訪問憑證（Personal Access Token），自行建立，以個人身份操作，可設定有效期和權限範圍。
- **OAuth 2.0**：使用者透過 OAuth 整合完成授權，短期有效、支援自動重新整理。

**PAT / OAuth 2.0 的附加參數：**
- `HAP-Appid`（Header）：標識來源應用，值為應用 ID，**應用級介面必填**。
- `orgId`（Query）：標識來源組織，值為組織 ID，**組織級介面必填**（如取得應用清單、建立應用）。

**Step 2: 設定 API 請求頭**

方式一 · AppKey + Sign（最常用）：

```javascript
const headers = {
  'Content-Type': 'application/json',
  'HAP-Appkey': '你的Appkey',
  'HAP-Sign': '你的Sign'
};
```

方式二 / 三 · PAT 或 OAuth 2.0（Bearer Token）：

```javascript
const headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer 你的access_token',
  'HAP-Appid': '應用ID'   // 應用級介面必填
};
```

---

#### **階段二: 建立應用結構**

**Step 3: 取得應用資訊(可選)**

檢視應用現有結構:

```bash
GET /v3/app/info
```

回傳應用的分組、工作表、自訂頁面等資訊。

---

**Step 4: 建立工作表**

```javascript
// 示例: 建立客戶資訊表
POST /v3/app/worksheets
{
  "name": "客戶資訊表",
  "alias": "customers",
  "fields": [
    {
      "name": "客戶名稱",
      "alias": "customer_name",
      "type": "Text",
      "isTitle": true,
      "required": true
    },
    {
      "name": "客戶型別",
      "alias": "customer_type",
      "type": "SingleSelect",
      "options": [
        {"value": "潛在客戶", "index": 1},
        {"value": "意向客戶", "index": 2},
        {"value": "成交客戶", "index": 3}
      ]
    },
    {
      "name": "年度預算",
      "alias": "annual_budget",
      "type": "Number",
      "precision": 2
    }
  ]
}

// 回傳: { "worksheet_id": "你的worksheetID" }
```

**關鍵點**:
- ✅ 一次性定義所有基礎欄位
- ✅ 使用 `alias` 便於後續引用
- ✅ 至少要有一個欄位設定 `isTitle: true`

---

**Step 5: 新增關聯欄位(如需要)**

如果需要關聯其他工作表:

```javascript
// 先建立目標表(如上一步)
// 然後建立關聯欄位

POST /v3/app/worksheets/{worksheet_id}
{
  "addFields": [
    {
      "name": "關聯客戶",
      "alias": "related_customer",
      "type": "Relation",
      "subType": "1",  // 單條關聯
      "dataSource": "你的worksheetID",  // 客戶表ID
      "relation": {
        "bidirectional": false,
        "showFields": ["customer_name", "customer_type"]
      }
    }
  ]
}
```

---

#### **階段三: 填充資料**

**Step 6: 準備選項欄位對映**

對於單選/多選欄位,需要先取得選項的 key:

```javascript
// 方法1: 查詢工作表結構
GET /v3/app/worksheets/{worksheet_id}

// 從回傳的 fields 中找到 options:
{
  "fields": [
    {
      "id": "customer_type",
      "type": "SingleSelect",
      "options": [
        {"key": "74c7b607-864d-4cc4-b401-28acba2636e9", "value": "成交客戶"},
        {"key": "f488d4db-5046-4b10-978f-7869c4c70a71", "value": "意向客戶"}
      ]
    }
  ]
}

// 建立對映表
const optionMap = {
  "成交客戶": "74c7b607-864d-4cc4-b401-28acba2636e9",
  "意向客戶": "f488d4db-5046-4b10-978f-7869c4c70a71"
};
```

---

**Step 7: 建立記錄**

```javascript
POST /v3/app/worksheets/{worksheet_id}/rows
{
  "fields": [
    {
      "id": "customer_name",
      "value": "niio科技有限公司"
    },
    {
      "id": "customer_type",
      "value": ["74c7b607-864d-4cc4-b401-28acba2636e9"]  // 使用選項key
    },
    {
      "id": "annual_budget",
      "value": 1000000.50
    }
  ],
  "triggerWorkflow": true  // 是否觸發工作流
}

// 回傳: { "row_id": "c74a29f0-f694-4501-9ba0-936e259daa9d" }
```

**關鍵點**:
- ⚠️ 選項欄位必須用 key,不能用顯示文字
- ⚠️ 選項欄位即使單選也要用陣列格式
- ✅ 數值欄位寫入時傳數字,讀取時回傳字串

---

**Step 8: 批次建立記錄(可選)**

```javascript
POST /v3/app/worksheets/{worksheet_id}/rows/batch
{
  "rows": [
    {
      "fields": [
        {"id": "customer_name", "value": "客戶A"},
        {"id": "customer_type", "value": ["key1"]}
      ]
    },
    {
      "fields": [
        {"id": "customer_name", "value": "客戶B"},
        {"id": "customer_type", "value": ["key2"]}
      ]
    }
  ],
  "triggerWorkflow": true
}
```

**建議**: 一次批次建立不超過 100 條記錄

---

#### **階段四: 查詢和分析資料**

**Step 9: 查詢記錄清單**

```javascript
POST /v3/app/worksheets/{worksheet_id}/rows/list
{
  "filter": {
    "type": "group",
    "logic": "AND",
    "children": [
      {
        "type": "condition",
        "field": "customer_type",
        "operator": "eq",
        "value": ["74c7b607-864d-4cc4-b401-28acba2636e9"]  // 成交客戶
      },
      {
        "type": "condition",
        "field": "annual_budget",
        "operator": "gte",
        "value": ["500000"]  // 預算>=50萬
      }
    ]
  },
  "sorts": [
    {
      "field": "annual_budget",
      "isAsc": false  // 降序
    }
  ],
  "pageIndex": 1,
  "pageSize": 20
}
```

---

**Step 10: 資料透視分析**

```javascript
POST /v3/app/worksheets/{worksheet_id}/rows/pivot
{
  "rows": [
    {
      "field": "customer_type",
      "displayName": "客戶型別"
    }
  ],
  "values": [
    {
      "field": "rowid",
      "aggregation": "COUNT",
      "displayName": "客戶數量"
    },
    {
      "field": "annual_budget",
      "aggregation": "SUM",
      "displayName": "預算總額"
    }
  ],
  "includeSummary": true
}
```

---

#### **階段五: 更新和維護資料**

**Step 11: 更新記錄**

```javascript
POST /v3/app/worksheets/{worksheet_id}/rows/{row_id}
{
  "fields": [
    {
      "id": "customer_type",
      "value": ["new-option-key"]  // 更改客戶型別
    },
    {
      "id": "annual_budget",
      "value": 1500000  // 更新預算
    }
  ],
  "triggerWorkflow": true
}
```

---

**Step 12: 刪除記錄**

```javascript
// 單條刪除
DELETE /v3/app/worksheets/{worksheet_id}/rows/{row_id}
{
  "permanent": false,  // false=邏輯刪除(可恢復), true=永久刪除
  "triggerWorkflow": true
}

// 批次刪除
DELETE /v3/app/worksheets/{worksheet_id}/rows/batch
{
  "rowIds": ["row-id-1", "row-id-2"],
  "permanent": false,
  "triggerWorkflow": true
}
```

⚠️ **警告**: `permanent: true` 會永久刪除資料,無法恢復!

---

### 0.3 API 呼叫最佳實踐

#### **初始化階段的建議步驟**

```javascript
// 1. 取得應用結構
const appInfo = await getAppInfo();

// 2. 取得所有工作表結構
const worksheets = {};
for (const ws of appInfo.worksheets) {
  worksheets[ws.alias] = await getWorksheetStructure(ws.worksheet_id);
}

// 3. 建立選項欄位對映
const optionMaps = {};
for (const [alias, structure] of Object.entries(worksheets)) {
  optionMaps[alias] = {};
  structure.fields.forEach(field => {
    if (field.type === 'SingleSelect' || field.type === 'MultipleSelect') {
      optionMaps[alias][field.alias] = {};
      field.options.forEach(opt => {
        optionMaps[alias][field.alias][opt.value] = opt.key;
      });
    }
  });
}

// 4. 快取欄位ID對映
const fieldMaps = {};
for (const [alias, structure] of Object.entries(worksheets)) {
  fieldMaps[alias] = {};
  structure.fields.forEach(field => {
    fieldMaps[alias][field.alias] = field.id;
  });
}
```

---

#### **執行時的建議**

1. **使用欄位ID而不是別名**: 效能更好
2. **快取選項對映**: 避免重複查詢
3. **合理使用分頁**: pageSize 建議 100-500
4. **批次操作分批**: 每批不超過 100 條
5. **非同步處理附件**: 上傳後等待 5-10 秒

---

### 0.4 常見場景快速參考

| 場景 | API 端點 | 關鍵參數 |
|-----|---------|---------|
| 建立工作表 | `POST /v3/app/worksheets` | fields |
| 新增欄位 | `POST /v3/app/worksheets/{id}` | addFields |
| 建立記錄 | `POST /v3/app/worksheets/{id}/rows` | fields |
| 批次建立 | `POST /v3/app/worksheets/{id}/rows/batch` | rows |
| 查詢記錄 | `POST /v3/app/worksheets/{id}/rows/list` | filter, sorts |
| 更新記錄 | `POST /v3/app/worksheets/{id}/rows/{row_id}` | fields |
| 批次更新 | `PUT /v3/app/worksheets/{id}/rows/batch` | rowIds, fields |
| 刪除記錄 | `DELETE /v3/app/worksheets/{id}/rows/{row_id}` | permanent |
| 批次刪除 | `DELETE /v3/app/worksheets/{id}/rows/batch` | rowIds, permanent |
| 透視分析 | `POST /v3/app/worksheets/{id}/rows/pivot` | rows, values |
| 查詢使用者 | `POST /v3/users/lookup` | name |
| 查詢部門 | `POST /v3/departments/lookup` | name |

---

### 0.5 關鍵概念速查

**欄位型別 (type)**:
- 基礎: `Text`, `Number`, `Date`, `Time`
- 選擇: `SingleSelect`, `MultipleSelect`
- 關係: `Relation`, `Collaborator`, `Department`
- 其他: `Attachment`, `Rating`

**篩選運算子 (operator)**:
- 比較: `eq`, `ne`, `gt`, `gte`, `lt`, `lte`
- 文字: `contains`, `startswith`, `endswith`
- 範圍: `between`, `in`
- 關聯(Relation): `in` / `eq`（值為 rowid 陣列）
- 部門(Department): `in` / `eq` / `notin` 等（詳見 2.1.1 對照表；V3 API 無 belongsto）
- 空值: `isempty`, `isnotempty`

**subType 參數**:
- Collaborator: `0`=單選, `1`=多選
- Relation: `1`=單條, `2`=多條
- Time: `1`=時:分, `6`=時:分:秒
- Date: `3`=年月日, `6`=年月日時分秒

---

## 一、建立工作表規範

### 1.1 基礎工作表建立

**API**: `POST /v3/app/worksheets`

**基本結構**:
```json
{
  "name": "工作表名稱",
  "alias": "worksheet_alias",  // 可選,建議使用英文別名
  "sectionId": "group-id",     // 可選,指定分組
  "fields": [
    // 欄位定義陣列
  ]
}
```

**示例 - 建立客戶資訊表**:
```json
{
  "name": "客戶資訊表",
  "alias": "customers",
  "fields": [
    {
      "name": "客戶名稱",
      "alias": "customer_name",
      "type": "Text",
      "isTitle": true,      // 標題欄位
      "required": true      // 必填
    },
    {
      "name": "客戶評級",
      "alias": "rating",
      "type": "Rating",
      "max": 5,             // 最大等級0-10
      "required": false
    }
  ]
}
```

---

### 1.2 特殊欄位型別處理

#### 1.2.1 單選/多選欄位 (SingleSelect/MultipleSelect)

**建立時必須提供選項**:

```json
{
  "name": "客戶型別",
  "alias": "customer_type",
  "type": "SingleSelect",
  "options": [
    {"value": "潛在客戶", "index": 1},
    {"value": "意向客戶", "index": 2},
    {"value": "成交客戶", "index": 3}
  ],
  "required": false
}
```

**關鍵點**:
- ✅ 必須提供 `options` 陣列
- ✅ 每個選項需要 `value` (顯示文字) 和 `index` (排序)
- ⚠️ 系統會自動為每個選項生成唯一的 `key` (UUID)
- ⚠️ 後續查詢/更新時必須使用 `key`,不能用 `value`

---

#### 1.2.2 關聯欄位 (Relation) ⭐重點

**關聯欄位設定項**:

| 參數 | 型別 | 必填 | 說明 |
|-----|------|------|------|
| `type` | string | ✅ | 必須為 "Relation" |
| `dataSource` | string | ✅ | 關聯的目標工作表ID |
| `subType` | string | ✅ | "1"=單條記錄, "2"=多條記錄 |
| `relation` | object | ❌ | 關聯設定詳情 |
| `relation.bidirectional` | boolean | ❌ | 是否雙向關聯 |
| `relation.showFields` | array | ❌ | 關聯卡片顯示的欄位ID清單 |

**示例 - 建立單條關聯欄位**:
```json
{
  "name": "關聯客戶",
  "alias": "related_customer",
  "type": "Relation",
  "subType": "1",                          // 單條記錄
  "dataSource": "你的worksheetID", // 目標表ID
  "relation": {
    "bidirectional": false,                // 單向關聯
    "showFields": [                        // 顯示欄位
      "customer_name",
      "customer_type"
    ]
  },
  "required": false
}
```

**示例 - 建立多條關聯欄位**:
```json
{
  "name": "關聯專案",
  "alias": "related_projects",
  "type": "Relation",
  "subType": "2",                          // 多條記錄
  "dataSource": "你的worksheetID2",
  "relation": {
    "bidirectional": true,                 // 雙向關聯
    "showFields": ["project_name", "project_status"]
  },
  "required": false
}
```

**⚠️ 關聯欄位重要注意事項**:

1. **dataSource不可修改**: 一旦建立,關聯的目標表不能更改,只能刪除重建
2. **必須先建立目標表**: `dataSource` 的工作表ID必須已存在
3. **雙向關聯自動建立**: `bidirectional: true` 會在目標表自動建立反向關聯欄位
4. **showFields可為空**: 不提供時使用目標表的標題欄位
5. **建議使用欄位ID**: `showFields` 使用欄位ID比別名更穩定

---

#### 1.2.3 成員欄位 (Collaborator)

```json
{
  "name": "負責人",
  "alias": "owner",
  "type": "Collaborator",
  "subType": "0",  // 0=單選, 1=多選
  "required": false
}
```

---

#### 1.2.4 日期/時間欄位 (Date/DateTime/Time)

**Date欄位 - subType控制精度**:

```json
{
  "name": "成立日期",
  "alias": "founded_date",
  "type": "Date",
  "subType": "3",  // 5=年, 4=年月, 3=年月日, 2=年月日時, 1=年月日時分, 6=年月日時分秒
  "required": false
}
```

**Time欄位**:
```json
{
  "name": "工作時間",
  "alias": "work_time",
  "type": "Time",
  "subType": "1",  // 1=時:分, 6=時:分:秒
  "required": false
}
```

---

#### 1.2.5 數值欄位 (Number)

```json
{
  "name": "年度預算",
  "alias": "annual_budget",
  "type": "Number",
  "precision": 2,  // 小數位數 0-14
  "required": false
}
```

---

#### 1.2.6 等級欄位 (Rating)

```json
{
  "name": "客戶評級",
  "alias": "customer_rating",
  "type": "Rating",
  "max": 5,  // 最大等級 0-10
  "required": false
}
```

---

#### 1.2.7 附件欄位 (Attachment)

```json
{
  "name": "附件",
  "alias": "attachments",
  "type": "Attachment",
  "required": false
}
```

**說明**: 附件欄位建立時無需額外參數

---

### 1.3 完整建立工作表示例

**場景**: 建立銷售機會表,包含關聯客戶

```json
{
  "name": "銷售機會表",
  "alias": "opportunities",
  "fields": [
    {
      "name": "機會名稱",
      "alias": "opportunity_name",
      "type": "Text",
      "isTitle": true,
      "required": true
    },
    {
      "name": "關聯客戶",
      "alias": "related_customer",
      "type": "Relation",
      "subType": "1",
      "dataSource": "你的worksheetID",  // 客戶表ID
      "relation": {
        "bidirectional": false,
        "showFields": ["customer_name", "customer_type"]
      },
      "required": true
    },
    {
      "name": "銷售階段",
      "alias": "stage",
      "type": "SingleSelect",
      "options": [
        {"value": "初次接觸", "index": 1},
        {"value": "需求確認", "index": 2},
        {"value": "方案報價", "index": 3},
        {"value": "商務談判", "index": 4},
        {"value": "贏單", "index": 5}
      ],
      "required": false
    },
    {
      "name": "預計金額",
      "alias": "expected_amount",
      "type": "Number",
      "precision": 2,
      "required": false
    },
    {
      "name": "預計成交日期",
      "alias": "close_date",
      "type": "Date",
      "subType": "3",
      "required": false
    },
    {
      "name": "成單機率",
      "alias": "win_probability",
      "type": "SingleSelect",
      "options": [
        {"value": "30%", "index": 1},
        {"value": "50%", "index": 2},
        {"value": "70%", "index": 3},
        {"value": "90%", "index": 4}
      ],
      "required": false
    }
  ]
}
```

---

## 二、欄位型別參數詳解

### 2.1 欄位型別對照表

| 欄位型別 | type值 | 必需參數 | 可選參數 | 說明 |
|---------|--------|---------|---------|------|
| 文字 | Text | name | alias, required, isTitle, isUnique, isReadOnly, isHidden, isHiddenOnCreate | 基礎文字欄位 |
| 數值 | Number | name | precision (0-14), alias, required | 支援小數 |
| 單選 | SingleSelect | name, options | alias, required | 必須提供選項 |
| 多選 | MultipleSelect | name, options | alias, required | 必須提供選項 |
| 日期 | Date | name | subType (5/4/3/2/1/6), alias, required | 不同精度 |
| 日期時間 | DateTime | name | subType (5/4/3/2/1/6), alias, required | 同Date,用於相容 |
| 時間 | Time | name | subType (1/6), alias, required | 時分或時分秒 |
| 成員 | Collaborator | name | subType (0/1), alias, required | 單選或多選 |
| 部門 | Department | name | subType (0/1), alias, required | 單選或多選部門 |
| 地區 | Region | name | alias, required | 省市區選擇 |
| 關聯記錄 | Relation | name, dataSource, subType | relation, alias, required | 必須指定目標表 |
| 附件 | Attachment | name | alias, required | 支援URL和base64 |
| 等級 | Rating | name | max (0-10), alias, required | 星級評分 |

---

### 2.1.1 完整欄位型別 / Code / 篩選運算子對照表（API 權威）

> ⭐ 本表是欄位 **Code** 與 **篩選運算子** 的權威依據。注意：**V3 API 不支援 `belongsto`**——部門(Department)/關聯(Relation) 等欄位一律使用本表列出的運算子（如 `in`、`eq`、`notin`）。`-` 表示該欄位不支援對應能力。

| Type | Code | 描述 | API建立 | API查詢 | 支援的篩選運算子 |
|------|------|------|:------:|:------:|------|
| Text | 2 | 文字 | ✓ | ✓ | `eq`, `ne`, `contains`, `concurrent`, `notcontains`, `startswith`, `notstartswith`, `endswith`, `notendswith`, `isempty`, `isnotempty` |
| PhoneNumber | 3 | 手機 | - | ✓ | 同 `Text` |
| LandlinePhone | 4 | 座機 | - | ✓ | 同 `Text` |
| Email | 5 | 郵箱 | - | ✓ | 同 `Text` |
| Number | 6 | 數值 | ✓ | ✓ | `eq`, `ne`, `gt`, `lt`, `ge`, `le`, `between`, `notbetween`, `isempty`, `isnotempty` |
| Certificate | 7 | 證件 | - | ✓ | 同 `Text` |
| Currency | 8 | 金額 | - | ✓ | 同 `Number` |
| SingleSelect | 9 | 單選 | ✓ | ✓ | `eq`, `ne`, `in`, `notin`, `isempty`, `isnotempty` |
| MultipleSelect | 10 | 多選 | ✓ | ✓ | `eq`, `ne`, `in`, `notin`, `concurrent`, `isempty`, `isnotempty` |
| Dropdown | 11 | 下拉 | - | ✓ | `eq`, `ne`, `in`, `notin`, `isempty`, `isnotempty` |
| Attachment | 14 | 附件 | ✓ | ✓ | `isempty`, `isnotempty` |
| Date | 15 | 日期 | ✓ | ✓ | `between`, `notbetween` |
| DateTime | 16 | 時間 | ✓ | ✓ | `between`, `notbetween` |
| Region | 19/23/24 | 地區 | - | ✓ | `eq`, `ne`, `between`, `notbetween`, `in`, `isempty`, `isnotempty` |
| DynamicLink | 21 | 自由連結 | - | ✓ | `isempty`, `isnotempty` |
| Divider | 22 | 分段 | - | - | - |
| AmountInWords | 25 | 大寫金額 | - | ✓ | 同 `Number` |
| Collaborator | 26 | 成員 | ✓ | ✓ | `eq`, `ne`, `in`, `notin`, `concurrent`, `isempty`, `isnotempty` |
| Department | 27 | 部門 | - | ✓ | `eq`, `ne`, `between`, `notbetween`, `in`, `notin`, `concurrent`, `isempty`, `isnotempty` |
| Rating | 28 | 等級 | - | ✓ | 同 `Number` |
| Relation | 29 | 關聯記錄 | ✓ | ✓ | `eq`, `ne`, `in`, `notin`, `concurrent`, `isempty`, `isnotempty` |
| Lookup | 30 | 他表欄位 | - | ✓ | - |
| Formula | 31 | 公式 | - | ✓ | 同 `Number` |
| Concatenate | 32 | 文字拼接 | - | ✓ | 同 `Text` |
| AutoNumber | 33 | 自動編號 | - | ✓ | 同 `Text` |
| SubTable | 34 | 子表 | - | ✓ | `isempty`, `isnotempty` |
| CascadingSelect | 35 | 級聯選擇 | - | ✓ | `eq`, `ne`, `between`, `notbetween`, `isempty`, `isnotempty` |
| Checkbox | 36 | 檢查框 | - | ✓ | `isempty`, `isnotempty` |
| Rollup | 37 | 彙總 | - | ✓ | 同 `Number` |
| DateFormula | 38 | 公式（日期） | - | ✓ | - |
| CodeScan | 39 | 掃碼 | - | ✓ | - |
| Location | 40 | 定位 | - | ✓ | `isempty`, `isnotempty` |
| RichText | 41 | 富文字 | - | ✓ | `isempty`, `isnotempty` |
| Signature | 42 | 簽名 | - | ✓ | `isempty`, `isnotempty` |
| OCR | 43 | 文字識別 | - | ✓ | - |
| Role | 44 | 角色 | - | ✓ | - |
| Embed | 45 | 嵌入 | - | - | - |
| Time | 46 | 時間 | ✓ | ✓ | `between`, `notbetween` |
| Barcode | 47 | 條碼 | - | ✓ | - |
| OrgRole | 48 | 組織角色 | - | ✓ | `eq`, `ne`, `in`, `notin`, `concurrent`, `isempty`, `isnotempty` |
| Button | 49 | API查詢(按鈕) | - | - | - |
| APIQuery | 50 | API查詢(下拉) | - | - | - |
| QueryRecord | 51 | 查詢記錄 | - | - | - |
| Section | 52 | 標籤頁 | - | - | - |
| FunctionFormula | 53 | 函式公式 | - | ✓ | - |
| CustomField | 54 | 自訂欄位 | - | - | - |
| Array | 10000003 | 陣列 (工作流) | - | - | - |
| Object | 10000006 | 物件 (工作流) | - | - | - |
| SimpleArray | 10000007 | 普通陣列 (工作流) | - | - | - |
| ObjectArray | 10000008 | 物件陣列 (工作流) | - | - | - |

---

### 2.2 subType參數詳解

**Collaborator (成員欄位)**:
- `"0"` - 單選成員
- `"1"` - 多選成員

**Relation (關聯欄位)**:
- `"1"` - 單條記錄
- `"2"` - 多條記錄

**Time (時間欄位)**:
- `"1"` - 時:分 (HH:mm)
- `"6"` - 時:分:秒 (HH:mm:ss)

**Date/DateTime (日期欄位)**:
- `"5"` - 年 (YYYY)
- `"4"` - 年月 (YYYY-MM)
- `"3"` - 年月日 (YYYY-MM-DD)
- `"2"` - 年月日時 (YYYY-MM-DD HH)
- `"1"` - 年月日時分 (YYYY-MM-DD HH:mm)
- `"6"` - 年月日時分秒 (YYYY-MM-DD HH:mm:ss)

---

### 2.3 欄位約束參數

| 參數 | 型別 | 說明 | 適用欄位 |
|-----|------|------|---------|
| `required` | boolean | 是否必填 | 所有欄位 |
| `isTitle` | boolean | 是否為標題欄位 | Text |
| `isUnique` | boolean | 是否唯一 | Text, Number |
| `isReadOnly` | boolean | 是否只讀 | 所有欄位 |
| `isHidden` | boolean | 是否隱藏 | 所有欄位 |
| `isHiddenOnCreate` | boolean | 建立時隱藏 | 所有欄位 |

---

## 三、建立/更新記錄規範

### 3.1 建立記錄 API

**API**: `POST /v3/app/worksheets/{worksheet_id}/rows`

**請求體結構**:
```json
{
  "fields": [
    {"id": "field_id_or_alias", "value": "對應值"}
  ],
  "triggerWorkflow": true  // 是否觸發工作流,預設true
}
```

---

### 3.2 triggerWorkflow 參數詳解 ⭐重要

`triggerWorkflow` 參數控制是否在資料操作時觸發工作表相關的工作流。

**適用範圍**:
- ✅ 建立記錄: `POST /v3/app/worksheets/{worksheet_id}/rows`
- ✅ 批次建立: `POST /v3/app/worksheets/{worksheet_id}/rows/batch`
- ✅ 更新記錄: `POST /v3/app/worksheets/{worksheet_id}/rows/{row_id}`
- ✅ 批次更新: `PUT /v3/app/worksheets/{worksheet_id}/rows/batch`
- ✅ 刪除記錄: `DELETE /v3/app/worksheets/{worksheet_id}/rows/{row_id}`
- ✅ 批次刪除: `DELETE /v3/app/worksheets/{worksheet_id}/rows/batch`

**參數說明**:

| 參數值 | 說明 | 預設值 | 使用場景 |
|-------|------|--------|----------|
| `true` | 觸發工作流 | ✅ 是 | 正常業務操作,需要執行自動化流程 |
| `false` | 不觸發工作流 | ❌ 否 | 資料遷移、批次初始化、測試資料 |

**工作流觸發時機**:

工作流根據觸發條件設定決定是否執行:
- **新增記錄時**: 觸發"當記錄被新增時"型別的工作流
- **更新記錄時**: 觸發"當記錄被更新時"型別的工作流
- **刪除記錄時**: 觸發"當記錄被刪除時"型別的工作流
- **欄位變更時**: 觸發特定欄位值變化的工作流

**使用建議**:

**✅ 應該設定為 `true` 的場景**:

1. **正常業務操作**
```javascript
// 建立銷售機會,觸發自動分配負責人工作流
await createRecord({
  fields: [...],
  triggerWorkflow: true  // 觸發工作流
});
```

2. **使用者提交表單**
```javascript
// 客戶提交訂單,觸發通知和審批流程
await createRecord({
  fields: orderData,
  triggerWorkflow: true
});
```

3. **需要自動化處理的操作**
```javascript
// 更新客戶狀態,觸發客戶跟進提醒
await updateRecord(worksheetId, rowId, {
  fields: [{id: "status", value: ["已成交"]}],
  triggerWorkflow: true  // 觸發跟進工作流
});
```

**❌ 應該設定為 `false` 的場景**:

1. **資料遷移和匯入**
```javascript
// 從舊系統遷移資料,不需要觸發通知
await batchCreateRecords({
  rows: migratedData,
  triggerWorkflow: false  // 避免大量工作流執行
});
```

2. **批次資料初始化**
```javascript
// 初始化測試資料
await batchCreateRecords({
  rows: testData,
  triggerWorkflow: false  // 不觸發工作流
});
```

3. **定時同步任務**
```javascript
// 定時從外部系統同步資料
async function syncExternalData() {
  const externalData = await fetchFromExternalSystem();

  await batchCreateRecords({
    rows: externalData,
    triggerWorkflow: false  // 避免重複觸發工作流
  });
}
```

4. **測試和除錯**
```javascript
// 測試資料寫入邏輯
await createRecord({
  fields: testFields,
  triggerWorkflow: false  // 測試時不觸發工作流
});
```

**效能影響**:

工作流執行會增加API響應時間:
- ✅ `triggerWorkflow: false` - API 響應快,通常 < 500ms
- ⚠️ `triggerWorkflow: true` - 需要等待工作流執行,可能需要 1-5 秒

**批次操作時的注意事項**:

```javascript
// ❌ 錯誤: 批次操作時觸發大量工作流可能導致超時
await batchCreateRecords({
  rows: Array(1000).fill({...}),  // 1000條記錄
  triggerWorkflow: true  // 會觸發1000次工作流!
});

// ✅ 正確: 分批處理,或關閉工作流觸發
// 方案1: 關閉工作流
await batchCreateRecords({
  rows: records,
  triggerWorkflow: false
});

// 方案2: 分批處理,控制併發
for (let i = 0; i < records.length; i += 50) {
  const batch = records.slice(i, i + 50);
  await batchCreateRecords({
    rows: batch,
    triggerWorkflow: true
  });
  await sleep(2000);  // 批次間延遲
}
```

**工作流觸發異常處理**:

```javascript
async function createRecordWithWorkflow(fields) {
  try {
    const result = await createRecord({
      fields: fields,
      triggerWorkflow: true
    });

    // API成功不代表工作流執行成功
    // 工作流異常不會影響記錄建立
    console.log('記錄建立成功:', result.row_id);

    // 如需確認工作流執行結果,需檢視工作流執行日誌

  } catch (error) {
    console.error('記錄建立失敗:', error);
  }
}
```

**⚠️ 重要提示**:

1. **記錄操作與工作流執行是非同步的**
   - API 回傳成功只表示記錄操作成功
   - 工作流在後臺非同步執行
   - 工作流執行失敗不會影響記錄操作

2. **工作流觸發條件**
   - 即使設定 `triggerWorkflow: true`,工作流也需要滿足自身設定的觸發條件
   - 例如:設定了"僅當狀態=已完成"的工作流,建立草稿記錄不會觸發

3. **工作流執行限制**
   - niio對工作流執行有頻率限制
   - 短時間內大量觸發可能被限流
   - 批次操作時建議關閉工作流觸發

4. **刪除操作的工作流**
   - 邏輯刪除(`permanent: false`)會觸發"記錄被刪除"工作流
   - 物理刪除(`permanent: true`)可能無法觸發工作流,因為記錄已徹底刪除

**最佳實踐**:

```javascript
// 封裝記錄建立函式,根據場景決定是否觸發工作流
async function smartCreateRecord(fields, options = {}) {
  const {
    isMigration = false,     // 是否為資料遷移
    isBatch = false,          // 是否為批次操作
    isTest = false            // 是否為測試
  } = options;

  // 自動判斷是否觸發工作流
  const triggerWorkflow = !(isMigration || (isBatch && fields.length > 50) || isTest);

  return await createRecord({
    fields: fields,
    triggerWorkflow: triggerWorkflow
  });
}

// 使用示例
await smartCreateRecord(fields, { isMigration: true });  // 遷移資料,不觸發
await smartCreateRecord(fields, { isBatch: true });       // 批次操作,自動判斷
await smartCreateRecord(fields);                          // 正常操作,觸發工作流
```

---

### 3.3 各欄位型別傳參示例

#### 3.3.1 文字欄位 (Text)

```json
{
  "id": "customer_name",
  "value": "niio科技有限公司"
}
```

---

#### 3.3.2 數值欄位 (Number)

**寫入**: 傳數字型別
```json
{
  "id": "annual_budget",
  "value": 1000000.50
}
```

**讀取**: 回傳字串
```json
{
  "annual_budget": "1000000.50"
}
```

⚠️ **注意**: 寫入數字,讀取字串

---

#### 3.3.3 單選欄位 (SingleSelect) ⭐重點

**寫入**: 必須傳選項key的陣列
```json
{
  "id": "customer_type",
  "value": ["74c7b607-864d-4cc4-b401-28acba2636e9"]  // 選項key
}
```

**讀取**: 回傳包含key和value的物件陣列
```json
{
  "customer_type": [
    {
      "key": "74c7b607-864d-4cc4-b401-28acba2636e9",
      "value": "成交客戶"
    }
  ]
}
```

**⚠️ 關鍵點**:
1. 即使是單選,也要用陣列 `["key"]`
2. 不能傳顯示文字 `["成交客戶"]`,必須用key
3. 新增選項時可設定 `type` 參數

**支援的type參數**:
```json
{
  "id": "customer_type",
  "type": "2",  // 1=不允許新增選項(預設), 2=允許新增選項
  "value": ["新選項名稱"]
}
```

---

#### 3.3.4 多選欄位 (MultipleSelect)

**寫入**: 傳多個選項key的陣列
```json
{
  "id": "customer_tags",
  "value": [
    "705de83e-b929-43e4-82ff-fff2f7dd6888",  // 重點客戶
    "422b4e56-263f-4bfa-bc88-77c09811080e",  // VIP
    "a2ef7406-a9b1-4fc8-ba02-33aa172998d0"   // 長期合作
  ]
}
```

**讀取**: 回傳物件陣列
```json
{
  "customer_tags": [
    {"key": "705de83e-b929-43e4-82ff-fff2f7dd6888", "value": "重點客戶"},
    {"key": "422b4e56-263f-4bfa-bc88-77c09811080e", "value": "VIP"},
    {"key": "a2ef7406-a9b1-4fc8-ba02-33aa172998d0", "value": "長期合作"}
  ]
}
```

---

#### 3.3.5 日期欄位 (Date)

**寫入**: 傳字串格式
```json
{
  "id": "founded_date",
  "value": "2025-01-11"  // YYYY-MM-DD
}
```

**日期時間格式**:
```json
{
  "id": "created_datetime",
  "value": "2025-01-11 14:30:45"  // YYYY-MM-DD HH:mm:ss
}
```

**讀取**: 回傳字串
```json
{
  "founded_date": "2025-01-11"
}
```

---

#### 3.3.6 時間欄位 (Time)

```json
{
  "id": "work_time",
  "value": "14:30:45"  // HH:mm:ss 或 HH:mm
}
```

---

#### 3.3.7 等級欄位 (Rating)

**寫入**: 傳字串格式的數字
```json
{
  "id": "customer_rating",
  "value": "5"  // 字串格式
}
```

**讀取**: 回傳字串
```json
{
  "customer_rating": "5"
}
```

---

#### 3.3.8 成員欄位 (Collaborator) ⭐重點

**寫入**: 傳使用者ID陣列
```json
{
  "id": "owner",
  "value": ["user-account-id-123"]  // 使用者ID,不是使用者名稱
}
```

**取得使用者ID**: 使用查詢使用者API
```bash
POST /v3/users/lookup
{
  "name": "張三"  // 精確匹配姓名
}

# 回傳
{
  "accountId": "user-account-id-123",
  "fullname": "張三",
  "email": "zhangsan@example.com"
}
```

**讀取**: 回傳使用者物件或物件陣列
```json
{
  "owner": {
    "accountId": "user-account-id-123",
    "fullname": "張三",
    "avatar": "https://...",
    "email": "zhangsan@example.com",
    "status": 1
  }
}
```

---

#### 3.3.9 部門欄位 (Department) ⭐新增

部門欄位用於選擇組織架構中的部門,與成員欄位類似,也支援單選和多選。

**欄位建立**:
```json
{
  "name": "所屬部門",
  "alias": "department",
  "type": "Department",
  "subType": "0",  // 0=單選, 1=多選
  "required": false
}
```

**單選部門寫入**: 傳部門ID陣列
```json
{
  "id": "department",
  "value": ["department-id-123"]  // 部門ID,不是部門名稱
}
```

**多選部門寫入**: 傳多個部門ID
```json
{
  "id": "departments",
  "value": [
    "department-id-123",
    "department-id-456"
  ]
}
```

**取得部門ID**: 使用查詢部門API

**方法1: 透過名稱查詢**
```bash
POST /v3/departments/lookup
{
  "name": "銷售部"  // 精確匹配部門名稱
}

# 回傳
{
  "success": true,
  "data": {
    "departmentId": "department-id-123",
    "departmentName": "銷售部",
    "parentId": "parent-dept-id",
    "level": 2
  }
}
```

**方法2: 取得部門清單**
```bash
GET /v3/departments

# 回傳組織架構樹
{
  "success": true,
  "data": [
    {
      "departmentId": "dept-001",
      "departmentName": "總裁辦",
      "children": [
        {
          "departmentId": "dept-002",
          "departmentName": "行政部"
        }
      ]
    },
    {
      "departmentId": "dept-003",
      "departmentName": "銷售中心",
      "children": [
        {
          "departmentId": "dept-004",
          "departmentName": "華東區銷售部"
        }
      ]
    }
  ]
}
```

**單選部門讀取**: 回傳部門物件
```json
{
  "department": {
    "departmentId": "department-id-123",
    "departmentName": "銷售部"
  }
}
```

**多選部門讀取**: 回傳部門物件陣列
```json
{
  "departments": [
    {
      "departmentId": "department-id-123",
      "departmentName": "銷售部"
    },
    {
      "departmentId": "department-id-456",
      "departmentName": "市場部"
    }
  ]
}
```

**部門欄位篩選**:
```json
{
  "type": "group",
  "logic": "AND",
  "children": [
    {
      "type": "condition",
      "field": "department",
      "operator": "eq",
      "value": ["department-id-123"]  // 使用部門ID
    }
  ]
}
```

**⚠️ 關鍵點**:
1. 必須使用部門ID,不能使用部門名稱
2. 需要先透過 `/v3/departments/lookup` 查詢部門ID
3. 部門ID格式通常為 UUID 字串
4. 支援單選(`subType: "0"`)和多選(`subType: "1"`)
5. 篩選時使用 `eq` 運算子

**使用示例**:
```javascript
// 1. 查詢部門ID
const dept = await findDepartment({ name: "銷售部" });
const deptId = dept.data.departmentId;

// 2. 建立記錄時設定部門
await createRecord({
  fields: [
    {
      "id": "department",
      "value": [deptId]
    }
  ]
});

// 3. 篩選某個部門的記錄
const records = await queryRecords({
  filter: {
    type: "group",
    logic: "AND",
    children: [{
      type: "condition",
      field: "department",
      operator: "eq",
      value: [deptId]
    }]
  }
});
```

---

#### 3.2.10 地區欄位 (Region) ⭐新增

地區欄位用於選擇省市區等地理區域,支援不同級別的地區選擇。

**欄位建立**:
```json
{
  "name": "所在地區",
  "alias": "region",
  "type": "Region",
  "required": false
}
```

**地區欄位寫入**: 傳地區編碼字串
```json
{
  "id": "region",
  "value": "310100"  // 上海市市轄區的地區編碼
}
```

**取得地區編碼**: 使用地區資訊API

**方法1: 透過名稱搜尋地區**
```bash
POST /v3/regions
{
  "search": "上海"
}

# 回傳匹配的地區清單
{
  "success": true,
  "data": [
    {
      "id": "310000",
      "name": "上海市",
      "parentId": null,
      "level": 1  // 1=省, 2=市, 3=區縣
    },
    {
      "id": "310100",
      "name": "市轄區",
      "parentId": "310000",
      "level": 2
    }
  ]
}
```

**方法2: 取得子級地區**
```bash
POST /v3/regions
{
  "id": "310000"  // 上海市的ID
}

# 回傳上海市下的所有區縣
{
  "success": true,
  "data": [
    {
      "id": "310100",
      "name": "市轄區",
      "parentId": "310000",
      "level": 2
    },
    {
      "id": "310101",
      "name": "黃浦區",
      "parentId": "310100",
      "level": 3
    },
    {
      "id": "310104",
      "name": "徐彙區",
      "parentId": "310100",
      "level": 3
    }
  ]
}
```

**地區欄位讀取**:
```json
{
  "region": {
    "id": "310100",
    "name": "上海市-市轄區",
    "code": "310100"
  }
}
```

**地區欄位篩選**:
```json
{
  "type": "group",
  "logic": "AND",
  "children": [
    {
      "type": "condition",
      "field": "region",
      "operator": "eq",
      "value": ["310100"]  // 使用地區編碼
    }
  ]
}
```

**資料透視分析中使用地區欄位**:

地區欄位支援按不同粒度進行統計:

```json
{
  "rows": [
    {
      "field": "region",
      "displayName": "所在地區",
      "granularity": 1,  // 1=省, 2=省/市, 3=省/市/區縣
      "includeEmpty": false
    }
  ],
  "values": [
    {
      "field": "rowid",
      "aggregation": "COUNT",
      "displayName": "客戶數量"
    }
  ]
}
```

**granularity 參數說明**:
- `1` - 按省統計(例如: 上海市、北京市)
- `2` - 按省/市統計(例如: 上海市-市轄區、北京市-市轄區)
- `3` - 按省/市/區縣統計(例如: 上海市-市轄區-黃浦區)

**⚠️ 關鍵點**:
1. 地區欄位值是地區編碼字串,不是地區名稱
2. 需要先透過 `/v3/regions` API 查詢地區編碼
3. 地區編碼是國家標準行政區劃程式碼
4. 篩選時使用 `eq` 運算子
5. 透視分析時可使用 `granularity` 參數控制統計粒度

**使用示例**:
```javascript
// 1. 搜尋地區編碼
const regions = await getRegions({ search: "上海" });
const regionCode = regions.data[0].id;  // "310000"

// 2. 建立記錄時設定地區
await createRecord({
  fields: [
    {
      "id": "region",
      "value": regionCode
    }
  ]
});

// 3. 篩選某個地區的記錄
const records = await queryRecords({
  filter: {
    type: "group",
    logic: "AND",
    children: [{
      type: "condition",
      field: "region",
      operator: "eq",
      value: [regionCode]
    }]
  }
});

// 4. 按省統計客戶分佈
const pivotData = await getPivotData({
  rows: [{
    field: "region",
    granularity: 1  // 按省統計
  }],
  values: [{
    field: "rowid",
    aggregation: "COUNT"
  }]
});
```

**地區資料層級結構示例**:
```
中國
  ├── 北京市 (110000) - 直轄市
  │    └── 市轄區 (110100)
  │         ├── 東城區 (110101)
  │         ├── 西城區 (110102)
  │         └── ...
  ├── 上海市 (310000) - 直轄市
  │    └── 市轄區 (310100)
  │         ├── 黃浦區 (310101)
  │         ├── 徐彙區 (310104)
  │         └── ...
  └── 廣東省 (440000) - 省
       ├── 廣州市 (440100)
       │    ├── 越秀區 (440103)
       │    └── ...
       ├── 深圳市 (440300)
       │    ├── 羅湖區 (440303)
       │    └── ...
       └── ...
```

**常見地區編碼**:
- 北京市: `110000`
- 上海市: `310000`
- 廣東省: `440000`
- 浙江省: `330000`

**💡 提示**:
- 建議快取常用地區的編碼對映,避免頻繁呼叫地區API
- 地區編碼是6位數字字串
- 直轄市的"市轄區"層級是必需的(例如上海市需要先選市轄區,再選具體區)
- 使用 `granularity` 參數可以實現靈活的地區維度分析

---

#### 3.2.11 關聯欄位 (Relation) ⭐重點

**單條關聯寫入**: 傳記錄ID陣列
```json
{
  "id": "related_customer",
  "value": ["945e6503-3823-4e91-9d84-a53f8bdd6fc5"]  // 客戶記錄ID
}
```

**多條關聯寫入**: 傳多個記錄ID
```json
{
  "id": "related_projects",
  "value": [
    "2df27f5e-6b8a-462c-bb6f-3de224b50bc3",
    "741c2c54-584f-49e4-9e96-01620da53e29",
    "c2e726e4-1392-4730-9c71-e5737f8503d8"
  ]
}
```

**單條關聯讀取**: 回傳物件陣列
```json
{
  "related_customer": [
    {
      "sid": "945e6503-3823-4e91-9d84-a53f8bdd6fc5",
      "name": "niio科技有限公司"
    }
  ]
}
```

**多條關聯讀取**: 回傳ID陣列
```json
{
  "related_projects": [
    "2df27f5e-6b8a-462c-bb6f-3de224b50bc3",
    "741c2c54-584f-49e4-9e96-01620da53e29",
    "c2e726e4-1392-4730-9c71-e5737f8503d8"
  ]
}
```

**取得關聯記錄完整資料**: 使用專用API
```bash
POST /v3/app/worksheets/{worksheet_id}/rows/{row_id}/relations/{field_id}

# 回傳完整關聯記錄詳情
{
  "data": {
    "rows": [
      {
        "rowid": "945e6503-3823-4e91-9d84-a53f8bdd6fc5",
        "customer_name": "niio科技有限公司",
        "customer_type": "成交客戶",
        "annual_budget": "1000000.00"
      }
    ],
    "total": 1
  }
}
```

---

#### 3.2.12 附件欄位 (Attachment) ⭐重點

**寫入**: 支援URL和base64兩種格式
```json
{
  "id": "attachments",
  "type": "0",  // 0=覆蓋已有附件, 1=追加新附件
  "value": [
    {
      "name": "產品宣傳冊.pdf",
      "url": "https://example.com/brochure.pdf"
    },
    {
      "name": "公司介紹.png",
      "url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
    }
  ]
}
```

**type參數**:
- `"0"` - 覆蓋模式:刪除已有附件,上傳新附件
- `"1"` - 追加模式:保留已有附件,新增附件

**讀取**: 回傳附件物件陣列
```json
{
  "attachments": [
    {
      "file_id": "7b866bd5-8541-40b7-976f-276081bdddcd",
      "file_name": "70f9836904834c3eb44c75c587c3fcac.pdf",
      "original_file_name": "產品宣傳冊.pdf",
      "file_size": 2048576,
      "file_type": 4,
      "DownloadUrl": "https://niio-assets.example.invalid/doc/20260111/xxx.pdf",
      "preview_url": "https://...",
      "thumbnail_full_path": "https://..."
    }
  ]
}
```

**⚠️ 重要提示**:
1. 附件上傳是**非同步處理**,通常需要5-10秒
2. API回傳成功不代表附件已上傳完成
3. 建議使用niio內部URL,外部URL可能有跨域限制
4. 支援base64編碼的圖片直接上傳

---

### 3.4 完整建立記錄示例

**場景**: 建立一條銷售機會記錄

```json
{
  "fields": [
    {
      "id": "opportunity_name",
      "value": "niio-企業版年度續費"
    },
    {
      "id": "related_customer",
      "value": ["c74a29f0-f694-4501-9ba0-936e259daa9d"]
    },
    {
      "id": "stage",
      "value": ["a9ac7988-7603-4f03-86d5-985bd1f0cb66"]  // 商務談判
    },
    {
      "id": "expected_amount",
      "value": 1200000
    },
    {
      "id": "close_date",
      "value": "2026-02-28"
    },
    {
      "id": "win_probability",
      "value": ["b9a6e559-7595-41f8-b0ad-febfb2daa4d5"]  // 90%
    },
    {
      "id": "competitor",
      "value": ""
    },
    {
      "id": "description",
      "value": "年度續約專案,增購100個賬戶"
    }
  ],
  "triggerWorkflow": true
}
```

---

### 3.5 更新記錄 API

**API**: `POST /v3/app/worksheets/{worksheet_id}/rows/{row_id}`

**請求體**: 與建立記錄相同
```json
{
  "fields": [
    {"id": "stage", "value": ["new-stage-key"]},
    {"id": "expected_amount", "value": 1500000}
  ],
  "triggerWorkflow": true
}
```

**⚠️ 注意**:
- 只傳需要更新的欄位
- 更新操作會覆蓋原有值(除附件type=1追加模式)
- 關聯欄位更新會覆蓋原有關聯關係

---

### 3.6 批次操作完整指南

批次操作可以顯著提高資料處理效率,但需要注意效能和錯誤處理。

---

#### 3.6.1 批次建立記錄

**API**: `POST /v3/app/worksheets/{worksheet_id}/rows/batch`

**請求體結構**:
```json
{
  "rows": [
    {
      "fields": [
        {"id": "customer_name", "value": "客戶A"},
        {"id": "customer_type", "value": ["option-key-1"]},
        {"id": "annual_budget", "value": 500000}
      ]
    },
    {
      "fields": [
        {"id": "customer_name", "value": "客戶B"},
        {"id": "customer_type", "value": ["option-key-2"]},
        {"id": "annual_budget", "value": 800000}
      ]
    },
    {
      "fields": [
        {"id": "customer_name", "value": "客戶C"},
        {"id": "customer_type", "value": ["option-key-1"]},
        {"id": "annual_budget", "value": 1200000}
      ]
    }
  ],
  "triggerWorkflow": true
}
```

**回傳結果**:
```json
{
  "success": true,
  "error_code": 1,
  "data": {
    "successCount": 3,
    "failCount": 0,
    "rows": [
      {"row_id": "abc123..."},
      {"row_id": "def456..."},
      {"row_id": "ghi789..."}
    ]
  }
}
```

**使用場景**:
- ✅ 初始資料匯入
- ✅ 資料遷移
- ✅ 定期批次同步
- ✅ Excel/CSV 資料批次上傳

**效能建議**:
- 📊 **單次數量限制**: 建議每批 50-100 條記錄
- 📊 **總量超過500條**: 分批處理,每批間隔 1-2 秒
- 📊 **包含關聯欄位**: 減少到每批 30-50 條
- 📊 **包含附件**: 建議單獨處理,不要批次

**錯誤處理示例**:
```javascript
async function batchCreateRecords(allData, batchSize = 100) {
  const results = [];
  const errors = [];

  // 分批處理
  for (let i = 0; i < allData.length; i += batchSize) {
    const batch = allData.slice(i, i + batchSize);

    try {
      const response = await createBatch({
        rows: batch,
        triggerWorkflow: true
      });

      results.push(...response.data.rows);

      // 記錄失敗的記錄
      if (response.data.failCount > 0) {
        errors.push({
          batchIndex: i / batchSize,
          failCount: response.data.failCount
        });
      }

      // 批次間延遲
      if (i + batchSize < allData.length) {
        await sleep(1000);  // 等待1秒
      }

    } catch (error) {
      console.error(`Batch ${i / batchSize} failed:`, error);
      errors.push({
        batchIndex: i / batchSize,
        error: error.message
      });
    }
  }

  return { results, errors };
}
```

---

#### 3.6.2 批次更新記錄

**API**: `PUT /v3/app/worksheets/{worksheet_id}/rows/batch`

**請求體結構**:
```json
{
  "rowIds": [
    "c74a29f0-f694-4501-9ba0-936e259daa9d",
    "945e6503-3823-4e91-9d84-a53f8bdd6fc5",
    "2df27f5e-6b8a-462c-bb6f-3de224b50bc3"
  ],
  "fields": [
    {
      "id": "stage",
      "value": ["new-stage-key"]
    },
    {
      "id": "rating",
      "value": "5"
    },
    {
      "id": "last_contact_date",
      "value": "2026-01-11"
    }
  ],
  "triggerWorkflow": true
}
```

**回傳結果**:
```json
{
  "success": true,
  "error_code": 1,
  "data": {
    "successCount": 3,
    "failCount": 0
  }
}
```

**⚠️ 重要限制**:
1. **相同值應用**: 批次更新會將相同的欄位值應用到所有指定記錄
2. **不支援差異化**: 如果需要為不同記錄設定不同值,必須單獨更新
3. **覆蓋模式**: 更新操作會覆蓋原有值(附件 type=1 除外)

**使用場景**:
- ✅ 批次修改狀態(如:全部設為"已完成")
- ✅ 批次分配負責人
- ✅ 批次更新同一欄位
- ❌ 不適合:為不同記錄設定不同值

**正確示例 - 批次分配負責人**:
```json
{
  "rowIds": ["id1", "id2", "id3"],
  "fields": [
    {
      "id": "owner",
      "value": ["user-account-id-123"]  // 將3條記錄的負責人都改為同一人
    }
  ]
}
```

**錯誤示例 - 嘗試差異化更新**:
```json
// ❌ 這樣不行!批次更新不支援為每條記錄設定不同值
{
  "rowIds": ["id1", "id2"],
  "fields": [
    {"id": "rating", "value": "5"},   // id1和id2都會被設為5
    {"id": "rating", "value": "3"}    // 後面的值會被忽略或覆蓋前面的
  ]
}
```

**需要差異化更新時的解決方案**:
```javascript
// 方案1: 單獨更新每條記錄
async function updateRecordsWithDifferentValues(updates) {
  const promises = updates.map(({rowId, fields}) =>
    updateRecord(worksheetId, rowId, { fields })
  );
  return await Promise.all(promises);
}

// 用法
await updateRecordsWithDifferentValues([
  { rowId: "id1", fields: [{ id: "rating", value: "5" }] },
  { rowId: "id2", fields: [{ id: "rating", value: "3" }] },
  { rowId: "id3", fields: [{ id: "rating", value: "4" }] }
]);
```

---

#### 3.6.3 批次刪除記錄

**API**: `DELETE /v3/app/worksheets/{worksheet_id}/rows/batch`

**請求體結構**:
```json
{
  "rowIds": [
    "c74a29f0-f694-4501-9ba0-936e259daa9d",
    "945e6503-3823-4e91-9d84-a53f8bdd6fc5"
  ],
  "permanent": false,  // false=邏輯刪除(可恢復), true=物理刪除(不可恢復)
  "triggerWorkflow": true
}
```

**回傳結果**:
```json
{
  "success": true,
  "error_code": 1,
  "data": {
    "successCount": 2,
    "failCount": 0
  }
}
```

**permanent 參數說明**:

| 參數值 | 刪除方式 | 可恢復 | 資料去向 | 使用場景 |
|-------|---------|--------|---------|---------|
| `false` (預設) | 邏輯刪除 | ✅ 可以 | 進入回收站 | 日常資料清理 |
| `true` | 物理刪除 | ❌ 不可恢復 | 永久刪除 | 敏感資料清除 |

**⚠️ 嚴重警告**:
```javascript
// 🚨 危險操作!永久刪除無法恢復!
DELETE /v3/app/worksheets/{worksheet_id}/rows/batch
{
  "rowIds": ["id1", "id2"],
  "permanent": true,  // ⚠️ 永久刪除!
  "triggerWorkflow": true
}
```

**安全刪除的最佳實踐**:
```javascript
async function safeDeleteRecords(rowIds, options = {}) {
  const {
    permanent = false,
    confirmCallback = null,
    backupFirst = true
  } = options;

  // 1. 永久刪除需要二次確認
  if (permanent) {
    const confirmed = confirmCallback
      ? await confirmCallback(rowIds.length)
      : confirm(`確定要永久刪除 ${rowIds.length} 條記錄嗎?此操作不可恢復!`);

    if (!confirmed) {
      return { cancelled: true };
    }
  }

  // 2. 可選:刪除前備份資料
  if (backupFirst) {
    const records = await getRecords({ rowIds });
    await saveBackup(records);  // 儲存到本地或備份庫
  }

  // 3. 執行刪除
  return await deleteBatch({
    rowIds,
    permanent,
    triggerWorkflow: true
  });
}
```

**使用場景**:
- ✅ 邏輯刪除(`permanent: false`):
  - 日常資料清理
  - 測試資料清理
  - 可能需要恢復的資料

- ⚠️ 物理刪除(`permanent: true`):
  - GDPR 資料刪除要求
  - 敏感資訊徹底清除
  - 已確認不再需要的歷史資料
  - **必須經過授權審批**

---

#### 3.6.4 批次操作效能最佳化

**推薦設定**:

```javascript
const BATCH_CONFIG = {
  // 基礎設定
  CREATE_BATCH_SIZE: 100,      // 建立批次大小
  UPDATE_BATCH_SIZE: 100,      // 更新批次大小
  DELETE_BATCH_SIZE: 100,      // 刪除批次大小

  // 特殊場景設定
  WITH_RELATION_SIZE: 50,      // 包含關聯欄位時
  WITH_ATTACHMENT_SIZE: 20,    // 包含附件時

  // 延遲設定
  BATCH_DELAY: 1000,           // 批次間延遲(毫秒)
  LARGE_BATCH_DELAY: 2000,     // 大批次延遲(>500條時)

  // 重試設定
  MAX_RETRIES: 3,              // 最大重試次數
  RETRY_DELAY: 3000            // 重試延遲
};
```

**效能最佳化技巧**:

1. **動態調整批次大小**:
```javascript
function calculateBatchSize(records) {
  let batchSize = BATCH_CONFIG.CREATE_BATCH_SIZE;

  // 檢查是否包含關聯欄位
  const hasRelation = records.some(r =>
    r.fields.some(f => f.type === 'Relation')
  );
  if (hasRelation) {
    batchSize = Math.min(batchSize, BATCH_CONFIG.WITH_RELATION_SIZE);
  }

  // 檢查是否包含附件
  const hasAttachment = records.some(r =>
    r.fields.some(f => f.type === 'Attachment')
  );
  if (hasAttachment) {
    batchSize = Math.min(batchSize, BATCH_CONFIG.WITH_ATTACHMENT_SIZE);
  }

  return batchSize;
}
```

2. **併發控制**:
```javascript
async function batchProcessWithConcurrency(items, batchSize, maxConcurrency = 3) {
  const batches = [];
  for (let i = 0; i < items.length; i += batchSize) {
    batches.push(items.slice(i, i + batchSize));
  }

  const results = [];
  for (let i = 0; i < batches.length; i += maxConcurrency) {
    const concurrentBatches = batches.slice(i, i + maxConcurrency);
    const batchResults = await Promise.all(
      concurrentBatches.map(batch => processBatch(batch))
    );
    results.push(...batchResults);

    // 併發批次之間也要有延遲
    if (i + maxConcurrency < batches.length) {
      await sleep(BATCH_CONFIG.BATCH_DELAY);
    }
  }

  return results;
}
```

3. **進度追蹤**:
```javascript
async function batchCreateWithProgress(records, onProgress) {
  const batchSize = calculateBatchSize(records);
  const totalBatches = Math.ceil(records.length / batchSize);
  let processedCount = 0;

  for (let i = 0; i < totalBatches; i++) {
    const batch = records.slice(i * batchSize, (i + 1) * batchSize);

    await createBatch({ rows: batch });

    processedCount += batch.length;
    onProgress({
      current: processedCount,
      total: records.length,
      percentage: Math.round((processedCount / records.length) * 100),
      batchIndex: i + 1,
      totalBatches
    });

    if (i < totalBatches - 1) {
      await sleep(BATCH_CONFIG.BATCH_DELAY);
    }
  }
}

// 使用
await batchCreateWithProgress(records, (progress) => {
  console.log(`進度: ${progress.percentage}% (${progress.current}/${progress.total})`);
});
```

---

#### 3.6.5 批次操作錯誤處理

**常見錯誤型別**:

| 錯誤碼 | 說明 | 處理方案 |
|-------|------|---------|
| `10` | 參數錯誤 | 檢查欄位ID、值格式 |
| `4` | 權限不足 | 檢查API權限設定 |
| `-1` | 通用失敗 | 檢視error_msg詳情 |
| `超時` | 請求超時 | 減少批次大小,重試 |

**健壯的批次處理實現**:
```javascript
async function robustBatchCreate(records, options = {}) {
  const {
    batchSize = 100,
    maxRetries = 3,
    onError = null,
    continueOnError = true
  } = options;

  const results = {
    success: [],
    failed: [],
    errors: []
  };

  for (let i = 0; i < records.length; i += batchSize) {
    const batch = records.slice(i, i + batchSize);
    let retries = 0;
    let success = false;

    while (retries < maxRetries && !success) {
      try {
        const response = await createBatch({ rows: batch });

        if (response.success) {
          results.success.push(...response.data.rows);
          success = true;
        } else {
          throw new Error(response.error_msg || 'Unknown error');
        }

      } catch (error) {
        retries++;

        const errorInfo = {
          batchIndex: i / batchSize,
          attempt: retries,
          error: error.message,
          records: batch
        };

        if (retries >= maxRetries) {
          // 達到最大重試次數
          results.failed.push(...batch);
          results.errors.push(errorInfo);

          if (onError) {
            await onError(errorInfo);
          }

          if (!continueOnError) {
            throw new Error(`Batch ${i / batchSize} failed after ${maxRetries} retries`);
          }
        } else {
          // 等待後重試
          console.log(`Batch ${i / batchSize} failed, retrying (${retries}/${maxRetries})...`);
          await sleep(BATCH_CONFIG.RETRY_DELAY * retries);
        }
      }
    }

    // 批次間延遲
    if (i + batchSize < records.length) {
      await sleep(BATCH_CONFIG.BATCH_DELAY);
    }
  }

  return results;
}

// 使用示例
const result = await robustBatchCreate(records, {
  batchSize: 50,
  maxRetries: 3,
  continueOnError: true,
  onError: async (errorInfo) => {
    // 記錄錯誤日誌
    await logError(errorInfo);
    // 傳送通知
    await notifyAdmin(`批次 ${errorInfo.batchIndex} 失敗`);
  }
});

console.log(`成功: ${result.success.length}, 失敗: ${result.failed.length}`);
if (result.failed.length > 0) {
  // 匯出失敗記錄
  await exportFailedRecords(result.failed);
}
```

**失敗記錄重試策略**:
```javascript
async function retryFailedRecords(failedRecords, originalBatchSize) {
  // 策略1: 減小批次大小
  const smallerBatchSize = Math.max(10, Math.floor(originalBatchSize / 2));

  // 策略2: 逐條重試
  if (failedRecords.length <= 10) {
    return await retryOneByOne(failedRecords);
  }

  // 策略3: 使用更小的批次
  return await robustBatchCreate(failedRecords, {
    batchSize: smallerBatchSize,
    maxRetries: 2
  });
}

async function retryOneByOne(records) {
  const results = { success: [], failed: [] };

  for (const record of records) {
    try {
      const response = await createRecord({ fields: record.fields });
      results.success.push(response.row_id);
    } catch (error) {
      results.failed.push({ record, error: error.message });
    }
  }

  return results;
}
```

---

#### 3.6.6 批次操作最佳實踐總結

**✅ 推薦做法**:

1. **合理分批**:
   - 基礎資料: 100條/批
   - 包含關聯: 50條/批
   - 包含附件: 20條/批,或單獨處理

2. **新增延遲**:
   - 批次間隔: 1-2秒
   - 大量資料: 增加到2-3秒

3. **錯誤處理**:
   - 實現重試機制
   - 記錄失敗資料
   - 提供恢復方案

4. **進度反饋**:
   - 顯示處理進度
   - 記錄處理日誌
   - 通知完成狀態

5. **效能監控**:
   - 記錄API響應時間
   - 監控成功率
   - 調整批次大小

**❌ 避免的做法**:

1. ❌ 一次性批次超過200條
2. ❌ 批次操作附件欄位
3. ❌ 不做錯誤處理和重試
4. ❌ 批次更新用於差異化更新
5. ❌ 物理刪除(`permanent: true`)未經確認
6. ❌ 無延遲連續批次請求
7. ❌ 忽略API回傳的error_code

---

## 四、查詢篩選規範

### 4.1 查詢記錄 API

**API**: `POST /v3/app/worksheets/{worksheet_id}/rows/list`

**基本請求體**:
```json
{
  "filter": {},           // 篩選條件,見下文
  "sorts": [],            // 排序,見下文
  "fields": [],           // 回傳欄位ID陣列,可選
  "search": "",           // 關鍵詞搜尋,可選
  "pageIndex": 1,         // 頁碼
  "pageSize": 100,        // 每頁數量,最大1000
  "viewId": "",           // 檢視ID,可選
  "includeSystemFields": false,  // 是否回傳系統欄位
  "useFieldIdAsKey": false       // 回傳資料key用欄位ID還是別名
}
```

---

### 4.2 Filter物件結構

**基礎結構**:
```typescript
Filter = {
  type: 'group' | 'condition';

  // type='group' 時的欄位
  logic?: 'AND' | 'OR';
  children?: Filter[];  // 子條件,最多兩層巢狀

  // type='condition' 時的欄位
  field?: string;       // 欄位ID或別名
  operator?: string;    // 運算子
  value?: any[];        // 值陣列
}
```

**規則**:
1. 頂層必須是 `group` 型別
2. 最多兩層巢狀: group → group → condition
3. 同一group的children必須型別一致(全是group或全是condition)
4. group必須指定 `logic` (AND/OR)
5. condition必須指定 `field`, `operator`
6. 部分運算子不需要 `value` (如isempty)

---

### 4.3 運算子完整清單

| 運算子 | 說明 | 需要value | value格式 | 適用欄位 |
|-------|------|----------|----------|---------|
| `eq` | 等於 | ✅ | `["值"]` | 所有型別 |
| `ne` | 不等於 | ✅ | `["值"]` | 所有型別 |
| `contains` | 包含 | ✅ | `["值"]` | Text, MultipleSelect |
| `notcontains` | 不包含 | ✅ | `["值"]` | Text, MultipleSelect |
| `startswith` | 開頭是 | ✅ | `["值"]` | Text |
| `endswith` | 結尾是 | ✅ | `["值"]` | Text |
| `gt` | 大於 | ✅ | `["值"]` | Number, Date |
| `gte` | 大於等於 | ✅ | `["值"]` | Number, Date |
| `lt` | 小於 | ✅ | `["值"]` | Number, Date |
| `lte` | 小於等於 | ✅ | `["值"]` | Number, Date |
| `between` | 介於之間 | ✅ | `["最小值", "最大值"]` | Number, Date |
| `isempty` | 為空 | ❌ | 不需要 | 所有型別 |
| `isnotempty` | 不為空 | ❌ | 不需要 | 所有型別 |
| `notin` | 不在其中 | ✅ | `["ID1", "ID2"]` | 多選/成員/部門/關聯等多值排除 |
| `in` | 在...中 | ✅ | `["值1", "值2"]` | 所有型別（Relation 用 rowid 陣列） |
| `concurrent` | 同時包含 | ✅ | `["值1", "值2"]` | MultipleSelect |

---

### 4.4 各欄位型別篩選示例

#### 4.4.1 文字欄位篩選

**包含查詢**:
```json
{
  "type": "group",
  "logic": "AND",
  "children": [
    {
      "type": "condition",
      "field": "customer_name",
      "operator": "contains",
      "value": ["niio"]
    }
  ]
}
```

**開頭匹配**:
```json
{
  "type": "condition",
  "field": "customer_name",
  "operator": "startswith",
  "value": ["北京"]
}
```

---

#### 4.4.2 數值欄位篩選 ⭐重點

**範圍查詢**:
```json
{
  "type": "condition",
  "field": "annual_budget",
  "operator": "between",
  "value": ["500000", "2000000"]  // ⚠️ 必須是字串陣列
}
```

**大於查詢**:
```json
{
  "type": "condition",
  "field": "expected_amount",
  "operator": "gt",
  "value": ["1000000"]  // ⚠️ 字串格式
}
```

**⚠️ 關鍵點**: 數值欄位的value必須是字串陣列!

---

#### 4.4.3 單選欄位篩選 ⭐⭐⭐重點

**等於查詢** (最常用):
```json
{
  "type": "condition",
  "field": "customer_type",
  "operator": "eq",
  "value": ["74c7b607-864d-4cc4-b401-28acba2636e9"]  // ⚠️ 必須用選項key
}
```

**❌ 錯誤示例**:
```json
{
  "type": "condition",
  "field": "customer_type",
  "operator": "eq",
  "value": ["成交客戶"]  // ❌ 不能用顯示文字!
}
```

**如何取得選項key**?

**方法1**: 先查詢一條記錄
```bash
POST /v3/app/worksheets/{worksheet_id}/rows/list
{
  "pageIndex": 1,
  "pageSize": 1
}

# 回傳資料中包含選項key
{
  "customer_type": [
    {"key": "74c7b607-864d-4cc4-b401-28acba2636e9", "value": "成交客戶"}
  ]
}
```

**方法2**: 查詢工作表結構
```bash
GET /v3/app/worksheets/{worksheet_id}

# 回傳欄位定義,包含options的key
{
  "fields": [
    {
      "id": "customer_type",
      "type": "SingleSelect",
      "options": [
        {"key": "74c7b607-864d-4cc4-b401-28acba2636e9", "value": "成交客戶"},
        {"key": "f488d4db-5046-4b10-978f-7869c4c70a71", "value": "意向客戶"}
      ]
    }
  ]
}
```

**💡 最佳實踐**: 應用初始化時快取所有選項欄位的key-value對映

---

#### 4.4.4 多選欄位篩選

**包含某個選項**:
```json
{
  "type": "condition",
  "field": "customer_tags",
  "operator": "contains",
  "value": ["705de83e-b929-43e4-82ff-fff2f7dd6888"]  // 重點客戶的key
}
```

**同時包含多個選項**:
```json
{
  "type": "condition",
  "field": "customer_tags",
  "operator": "concurrent",
  "value": [
    "705de83e-b929-43e4-82ff-fff2f7dd6888",  // 重點客戶
    "422b4e56-263f-4bfa-bc88-77c09811080e"   // VIP
  ]
}
```

---

#### 4.4.5 日期欄位篩選

**日期範圍**:
```json
{
  "type": "condition",
  "field": "founded_date",
  "operator": "between",
  "value": ["2020-01-01", "2025-12-31"]
}
```

**晚於某日期**:
```json
{
  "type": "condition",
  "field": "close_date",
  "operator": "gte",
  "value": ["2026-01-01"]
}
```

**日期格式**: `YYYY-MM-DD` 或 `YYYY-MM-DD HH:mm:ss`

---

#### 4.4.6 關聯欄位篩選 ⭐⭐重點

**屬於某個關聯記錄**:
```json
{
  "type": "condition",
  "field": "related_customer",
  "operator": "eq",  // 單值用 eq
  "value": ["945e6503-3823-4e91-9d84-a53f8bdd6fc5"]  // 客戶記錄rowid
}
```

**屬於多個關聯記錄之一**:
```json
{
  "type": "condition",
  "field": "related_customer",
  "operator": "in",  // 多值用 in
  "value": [
    "945e6503-3823-4e91-9d84-a53f8bdd6fc5",
    "c74a29f0-f694-4501-9ba0-936e259daa9d"
  ]
}
```

**⚠️ 關鍵點**:
1. 關聯欄位用 `in` 或 `eq` 運算子
2. V3 API 不支援 belongsto；部門(Department)欄位用 in / eq / notin 等（見 2.1.1 對照表）
3. value 傳入關聯記錄的 rowid 陣列

---

#### 4.4.7 成員欄位篩選

```json
{
  "type": "condition",
  "field": "owner",
  "operator": "eq",
  "value": ["user-account-id-123"]  // 使用者ID,不是姓名
}
```

---

#### 4.4.8 等級欄位篩選

```json
{
  "type": "condition",
  "field": "customer_rating",
  "operator": "gte",
  "value": ["4"]  // 字串格式
}
```

---

### 4.5 組合條件示例

#### 4.5.1 簡單AND條件

**查詢**: 評級≥4星 且 客戶型別=成交客戶

```json
{
  "type": "group",
  "logic": "AND",
  "children": [
    {
      "type": "condition",
      "field": "customer_rating",
      "operator": "gte",
      "value": ["4"]
    },
    {
      "type": "condition",
      "field": "customer_type",
      "operator": "eq",
      "value": ["74c7b607-864d-4cc4-b401-28acba2636e9"]
    }
  ]
}
```

---

#### 4.5.2 簡單OR條件

**查詢**: 客戶型別=成交客戶 或 客戶型別=意向客戶

```json
{
  "type": "group",
  "logic": "OR",
  "children": [
    {
      "type": "condition",
      "field": "customer_type",
      "operator": "eq",
      "value": ["74c7b607-864d-4cc4-b401-28acba2636e9"]  // 成交
    },
    {
      "type": "condition",
      "field": "customer_type",
      "operator": "eq",
      "value": ["f488d4db-5046-4b10-978f-7869c4c70a71"]  // 意向
    }
  ]
}
```

---

#### 4.5.3 巢狀條件 (AND + OR)

**查詢**: (型別=成交 或 型別=意向) 且 預算>50萬

```json
{
  "type": "group",
  "logic": "AND",
  "children": [
    {
      "type": "group",
      "logic": "OR",
      "children": [
        {
          "type": "condition",
          "field": "customer_type",
          "operator": "eq",
          "value": ["74c7b607-864d-4cc4-b401-28acba2636e9"]
        },
        {
          "type": "condition",
          "field": "customer_type",
          "operator": "eq",
          "value": ["f488d4db-5046-4b10-978f-7869c4c70a71"]
        }
      ]
    },
    {
      "type": "condition",
      "field": "annual_budget",
      "operator": "gt",
      "value": ["500000"]
    }
  ]
}
```

---

#### 4.5.4 複雜業務場景

**查詢**: 網際網路行業的成交客戶,且(預算>100萬 或 評級=5星)

```json
{
  "type": "group",
  "logic": "AND",
  "children": [
    {
      "type": "condition",
      "field": "industry",
      "operator": "eq",
      "value": ["4f28cae6-6a76-4b0b-b6e8-62cc724c677d"]  // 網際網路
    },
    {
      "type": "condition",
      "field": "customer_type",
      "operator": "eq",
      "value": ["74c7b607-864d-4cc4-b401-28acba2636e9"]  // 成交客戶
    },
    {
      "type": "group",
      "logic": "OR",
      "children": [
        {
          "type": "condition",
          "field": "annual_budget",
          "operator": "gt",
          "value": ["1000000"]
        },
        {
          "type": "condition",
          "field": "customer_rating",
          "operator": "eq",
          "value": ["5"]
        }
      ]
    }
  ]
}
```

---

### 4.6 排序 (Sorts)

**基本格式**:
```json
{
  "sorts": [
    {
      "field": "annual_budget",
      "isAsc": false  // false=降序, true=升序
    },
    {
      "field": "customer_rating",
      "isAsc": false
    }
  ]
}
```

**多欄位排序**: 按陣列順序優先順序排序

---

### 4.7 完整查詢示例

**業務場景**: 查詢網際網路行業的高價值客戶,按預算降序

```json
{
  "filter": {
    "type": "group",
    "logic": "AND",
    "children": [
      {
        "type": "condition",
        "field": "industry",
        "operator": "eq",
        "value": ["4f28cae6-6a76-4b0b-b6e8-62cc724c677d"]
      },
      {
        "type": "condition",
        "field": "customer_rating",
        "operator": "gte",
        "value": ["4"]
      },
      {
        "type": "condition",
        "field": "annual_budget",
        "operator": "gt",
        "value": ["500000"]
      }
    ]
  },
  "sorts": [
    {
      "field": "annual_budget",
      "isAsc": false
    }
  ],
  "fields": ["customer_name", "customer_type", "annual_budget", "customer_rating"],
  "pageIndex": 1,
  "pageSize": 20,
  "includeSystemFields": false
}
```

---

## 五、資料透視分析規範

### 5.1 透視分析 API

**API**: `POST /v3/app/worksheets/{worksheet_id}/rows/pivot`

**基本請求體**:
```json
{
  "rows": [],       // 行維度
  "columns": [],    // 列維度(可選)
  "values": [],     // 值/指標
  "filter": {},     // 篩選條件(可選)
  "sorts": [],      // 排序(可選)
  "includeSummary": true,  // 是否包含彙總
  "pageIndex": 1,
  "pageSize": 1000
}
```

---

### 5.2 維度設定

**行/列維度結構**:
```json
{
  "field": "industry",          // 欄位ID或別名
  "displayName": "所屬行業",    // 顯示名稱(可選)
  "granularity": 1,             // 粒度(日期/地區欄位)
  "includeEmpty": false         // 是否包含空值
}
```

**granularity參數** (僅日期和地區欄位):

**日期欄位**:
- `1` - 按天
- `2` - 按周
- `3` - 按月

**地區欄位**:
- `1` - 省
- `2` - 省/市
- `3` - 省/市/區縣

---

### 5.3 值/指標設定

**值設定結構**:
```json
{
  "field": "annual_budget",     // 欄位ID或別名
  "aggregation": "SUM",         // 聚合函式
  "displayName": "預算總額",    // 顯示名稱(可選)
  "includeEmpty": false         // 是否包含空值
}
```

**聚合函式** (不區分大小寫):

| 函式 | 說明 | 適用欄位 |
|-----|------|---------|
| `COUNT` | 計數 | 所有欄位 |
| `DISTINCTCOUNT` | 去重計數 | 所有欄位 |
| `SUM` | 求和 | Number |
| `AVG` | 平均值 | Number |
| `MIN` | 最小值 | Number, Date |
| `MAX` | 最大值 | Number, Date |

**⚠️ 注意**:
- 統計行數時,`field` 使用 `"rowid"`
- `aggregation` 不區分大小寫

---

### 5.4 透視分析示例

#### 5.4.1 單維度統計

**場景**: 按行業統計客戶數量和預算總額

```json
{
  "rows": [
    {
      "field": "industry",
      "displayName": "所屬行業",
      "includeEmpty": false
    }
  ],
  "values": [
    {
      "field": "rowid",
      "aggregation": "COUNT",
      "displayName": "客戶數量"
    },
    {
      "field": "annual_budget",
      "aggregation": "SUM",
      "displayName": "預算總額"
    }
  ],
  "includeSummary": true,
  "pageIndex": 1,
  "pageSize": 50
}
```

**回傳結果**:
```json
{
  "data": {
    "pivot": [
      {
        "rows": {"industry": "網際網路"},
        "values": {"rowid": 4.0, "annual_budget": 2150000.0}
      },
      {
        "rows": {"industry": "金融"},
        "values": {"rowid": 1.0, "annual_budget": 2000000.0}
      }
    ],
    "summary": {
      "rowid": 12.0,
      "annual_budget": 7900000.0
    }
  }
}
```

---

#### 5.4.2 多指標統計

**場景**: 按銷售階段統計機會的數量、金額總計、平均金額

```json
{
  "rows": [
    {
      "field": "opportunity_stage",
      "displayName": "銷售階段"
    }
  ],
  "values": [
    {
      "field": "rowid",
      "aggregation": "COUNT",
      "displayName": "機會數量"
    },
    {
      "field": "expected_amount",
      "aggregation": "SUM",
      "displayName": "金額總計"
    },
    {
      "field": "expected_amount",
      "aggregation": "AVG",
      "displayName": "平均金額"
    }
  ],
  "includeSummary": true
}
```

**回傳結果**:
```json
{
  "data": {
    "pivot": [
      {
        "rows": {"opportunity_stage": "商務談判"},
        "values": {
          "rowid": 3.0,
          "expected_amount": 2710000.0,
          "expected_amount_avg": 903333.33
        }
      }
    ],
    "summary": {
      "rowid": 10.0,
      "expected_amount": 8990000.0,
      "expected_amount_avg": 899000.0
    }
  }
}
```

---

#### 5.4.3 多維度交叉分析

**場景**: 按客戶型別和行業交叉統計客戶數

```json
{
  "rows": [
    {
      "field": "customer_type",
      "displayName": "客戶型別"
    },
    {
      "field": "industry",
      "displayName": "所屬行業"
    }
  ],
  "values": [
    {
      "field": "rowid",
      "aggregation": "COUNT",
      "displayName": "客戶數"
    }
  ],
  "includeSummary": true
}
```

**回傳結果**: 二維交叉資料
```json
{
  "data": {
    "pivot": [
      {
        "rows": {
          "customer_type": "成交客戶",
          "industry": "網際網路"
        },
        "values": {"rowid": 3.0}
      },
      {
        "rows": {
          "customer_type": "意向客戶",
          "industry": "製造業"
        },
        "values": {"rowid": 2.0}
      }
    ],
    "summary": {"rowid": 12.0}
  }
}
```

---

#### 5.4.4 帶篩選的透視分析

**場景**: 統計2026年Q1預計成交的機會

```json
{
  "filter": {
    "type": "group",
    "logic": "AND",
    "children": [
      {
        "type": "condition",
        "field": "expected_close_date",
        "operator": "between",
        "value": ["2026-01-01", "2026-03-31"]
      }
    ]
  },
  "rows": [
    {
      "field": "opportunity_stage",
      "displayName": "銷售階段"
    }
  ],
  "values": [
    {
      "field": "rowid",
      "aggregation": "COUNT",
      "displayName": "機會數量"
    },
    {
      "field": "expected_amount",
      "aggregation": "SUM",
      "displayName": "金額總計"
    }
  ],
  "includeSummary": true
}
```

---

## 六、關聯欄位完整指南

### 6.1 關聯欄位設計原則

**建立關聯欄位前需考慮**:
1. 關聯方向:單向還是雙向?
2. 關聯數量:單條還是多條?
3. 顯示欄位:關聯卡片顯示哪些資訊?
4. 資料依賴:目標表必須先存在

---

### 6.2 關聯欄位建立步驟

**Step 1**: 建立目標工作表(如客戶表)
```json
{
  "name": "客戶資訊表",
  "fields": [
    {"name": "客戶名稱", "type": "Text", "isTitle": true},
    {"name": "客戶型別", "type": "SingleSelect", "options": [...]}
  ]
}

// 回傳: {"worksheet_id": "你的worksheetID"}
```

**Step 2**: 在源工作表建立關聯欄位(如機會表)
```json
{
  "name": "銷售機會表",
  "fields": [
    {"name": "機會名稱", "type": "Text", "isTitle": true},
    {
      "name": "關聯客戶",
      "alias": "related_customer",
      "type": "Relation",
      "subType": "1",  // 單條關聯
      "dataSource": "你的worksheetID",  // 客戶表ID
      "relation": {
        "bidirectional": false,
        "showFields": ["customer_name", "customer_type"]
      }
    }
  ]
}
```

---

### 6.3 單向 vs 雙向關聯

**單向關聯** (`bidirectional: false`):
- 只在源表建立關聯欄位
- 目標表不會自動建立反向欄位
- 適用場景:機會→客戶,任務→專案

**雙向關聯** (`bidirectional: true`):
- 源表和目標表都有關聯欄位
- 系統自動在目標表建立反向欄位
- 適用場景:客戶↔聯絡人,專案↔任務

**示例 - 雙向關聯**:
```json
{
  "name": "關聯專案",
  "type": "Relation",
  "subType": "2",  // 多條關聯
  "dataSource": "project-table-id",
  "relation": {
    "bidirectional": true,  // 雙向
    "showFields": ["project_name", "project_status"]
  }
}
```

**效果**:
- 聯絡人表:顯示"關聯專案"欄位
- 專案表:自動建立"關聯聯絡人"反向欄位

---

### 6.4 關聯欄位寫入完整流程

**場景**: 為銷售機會關聯客戶

**Step 1**: 查詢客戶記錄,取得rowid
```bash
POST /v3/app/worksheets/你的worksheetID/rows/list
{
  "filter": {
    "type": "group",
    "logic": "AND",
    "children": [
      {
        "type": "condition",
        "field": "customer_name",
        "operator": "contains",
        "value": ["niio"]
      }
    ]
  },
  "pageSize": 1
}

# 回傳
{
  "data": {
    "rows": [
      {"rowid": "c74a29f0-f694-4501-9ba0-936e259daa9d", ...}
    ]
  }
}
```

**Step 2**: 建立機會記錄,傳入客戶rowid
```bash
POST /v3/app/worksheets/你的worksheetID2/rows
{
  "fields": [
    {
      "id": "opportunity_name",
      "value": "niio-年度續費"
    },
    {
      "id": "related_customer",
      "value": ["c74a29f0-f694-4501-9ba0-936e259daa9d"]  // 客戶rowid
    }
  ]
}
```

**Step 3**: 讀取驗證
```bash
GET /v3/app/worksheets/你的worksheetID2/rows/{row_id}

# 回傳
{
  "related_customer": [
    {
      "sid": "c74a29f0-f694-4501-9ba0-936e259daa9d",
      "name": "niio科技有限公司"
    }
  ]
}
```

---

### 6.5 取得關聯記錄完整資料

#### 6.5.1 關聯欄位回傳的資料結構

當讀取包含關聯欄位的記錄時,niio API 回傳的資料結構如下:

```javascript
{
  "示例控制元件ID": [  // 關聯欄位ID
    {
      "sid": "9dd9272b-e7e5-40d5-8a6d-d2403d1e45c2",  // 關聯記錄的ID (等同於 rowid)
      "name": "實木衣櫃"  // 關聯記錄的標題欄位值
    }
  ]
}
```

**關鍵屬性說明**:
- **`sid`**: 關聯記錄的唯一識別符號,等同於目標表中的 `rowid`
- **`name`**: 關聯記錄的標題欄位值(僅顯示用途)

**⚠️ 重要提示**:
- 預設情況下,關聯欄位只回傳 `sid` 和 `name` 兩個屬性
- 如果需要展示關聯表的其他資訊(如圖片、價格、描述等),需要進行**深度查詢**
- 深度查詢步驟:
  1. 找到該關聯欄位對應的目標工作表 ID
  2. 使用 `sid` (等同於 `rowid`) 去目標表查詢完整資料

---

#### 6.5.2 方法1: 使用 get_record_relations API (推薦)

**適用場景**: 取得單條記錄的關聯詳情

```bash
POST /v3/app/worksheets/{worksheet_id}/rows/{row_id}/relations/{field_id}
{
  "pageIndex": 1,
  "pageSize": 10,
  "isReturnSystemFields": false
}

# 回傳完整關聯記錄詳情
{
  "data": {
    "rows": [
      {
        "rowid": "c74a29f0-f694-4501-9ba0-936e259daa9d",
        "customer_name": "niio科技有限公司",
        "customer_type": [{"key": "...", "value": "成交客戶"}],
        "annual_budget": "1000000.00",
        "customer_rating": "5"
      }
    ],
    "total": 1
  }
}
```

**優點**: 一次請求取得完整資料,無需手動查詢目標表

---

#### 6.5.3 方法2: 先讀取關聯ID,再查詢目標表

**適用場景**: 批次查詢多條記錄的關聯詳情(避免 N+1 查詢問題)

**Step 1**: 讀取包含關聯欄位的記錄
```bash
GET /v3/app/worksheets/你的worksheetID2/rows/{row_id}

# 回傳
{
  "related_customer": [
    {
      "sid": "c74a29f0-f694-4501-9ba0-936e259daa9d",
      "name": "niio科技有限公司"
    }
  ]
}
```

**Step 2**: 使用 `sid` 查詢目標表完整資料

⚠️ **關鍵**: 使用 `rowid` 欄位 + `in` 運算子進行查詢

```bash
POST /v3/app/worksheets/你的worksheetID/rows/list
{
  "filter": {
    "type": "group",
    "logic": "AND",
    "children": [
      {
        "type": "condition",
        "field": "rowid",  // ⚠️ 使用系統欄位 rowid
        "operator": "in",  // ⚠️ 使用 in 運算子
        "value": ["c74a29f0-f694-4501-9ba0-936e259daa9d"]  // 傳入 sid 值
      }
    ]
  }
}

# 回傳完整資料
{
  "data": {
    "rows": [
      {
        "rowid": "c74a29f0-f694-4501-9ba0-936e259daa9d",
        "customer_name": "niio科技有限公司",
        "customer_type": [{"key": "...", "value": "成交客戶"}],
        "customer_logo": [{"downloadUrl": "https://..."}],
        "annual_budget": "1000000.00",
        "customer_rating": "5",
        "customer_address": "上海市徐彙區"
      }
    ]
  }
}
```

---

#### 6.5.4 批次查詢最佳化示例

**場景**: 產品清單頁面,需要顯示每個產品的完整分類資訊(包括分類圖示、描述等)

**問題**: 如果有 100 個產品,逐個查詢分類會產生 N+1 查詢問題(1次產品查詢 + N次分類查詢)

**解決方案**: 批次收集所有分類 ID,一次性查詢所有分類

```javascript
// Step 1: 取得產品清單
const products = await getRows('products-worksheet-id', {
  pageSize: 100
});

// Step 2: 收集所有產品的分類 ID (使用 Set 自動去重)
const categoryIds = new Set();
products.rows.forEach(product => {
  const categories = product['category_field_id'];  // 關聯欄位
  if (Array.isArray(categories)) {
    categories.forEach(cat => {
      categoryIds.add(cat.sid);  // 收集 sid
    });
  }
});

// Step 3: 批次查詢所有分類的完整資料 (1次請求!)
const categoriesData = await getRows('categories-worksheet-id', {
  filter: {
    type: 'group',
    logic: 'AND',
    children: [{
      type: 'condition',
      field: 'rowid',
      operator: 'in',
      value: Array.from(categoryIds)  // 傳入所有 sid 陣列
    }]
  }
});

// Step 4: 建立分類 ID → 分類資料的對映 (O(1) 查詢)
const categoryMap = {};
categoriesData.rows.forEach(cat => {
  categoryMap[cat.rowid] = cat;
});

// Step 5: 渲染產品清單,直接從 map 中取分類資料
products.rows.forEach(product => {
  const categories = product['category_field_id'];
  const categoryData = categoryMap[categories[0].sid];

  console.log({
    productName: product.name,
    categoryName: categoryData.name,
    categoryIcon: categoryData.icon[0].downloadUrl,
    categoryDesc: categoryData.description
  });
});
```

**效能對比**:
- ❌ 逐個查詢: 1 + 100 = 101 次 API 請求
- ✅ 批次查詢: 1 + 1 = 2 次 API 請求 (效能提升 50 倍!)

---

#### 6.5.5 方法選擇建議

| 場景 | 推薦方法 | 原因 |
|------|---------|------|
| 單條記錄詳情頁 | 方法1 (get_record_relations) | 簡單直接,一次請求 |
| 清單頁批次渲染 | 方法2 (批次查詢) | 避免 N+1 查詢,效能最優 |
| 需要自訂篩選條件 | 方法2 | 可以在查詢目標表時新增額外篩選 |
| 只需要顯示 name | 直接使用 | 無需額外查詢 |

---

### 6.6 關聯欄位更新

**覆蓋關聯**:
```json
{
  "fields": [
    {
      "id": "related_customer",
      "value": ["new-customer-id"]  // 覆蓋原有關聯
    }
  ]
}
```

**清空關聯**:
```json
{
  "fields": [
    {
      "id": "related_customer",
      "value": []  // 空陣列=清空關聯
    }
  ]
}
```

**多條關聯追加**: 需要先讀取原有ID,再合併
```bash
# Step 1: 讀取原有關聯
GET /v3/app/worksheets/{worksheet_id}/rows/{row_id}
# 回傳: {"related_projects": ["id1", "id2"]}

# Step 2: 合併新ID並更新
POST /v3/app/worksheets/{worksheet_id}/rows/{row_id}
{
  "fields": [
    {
      "id": "related_projects",
      "value": ["id1", "id2", "id3"]  // 原有+新增
    }
  ]
}
```

---

### 6.7 關聯欄位常見問題

**Q1: 關聯欄位回傳的 `sid` 和 `name` 有什麼區別?**

- **`sid`**: 關聯記錄的唯一識別符號,等同於目標表的 `rowid`,用於查詢完整資料
- **`name`**: 關聯記錄的標題欄位值,僅用於顯示

**關鍵理解**:
```javascript
// 讀取產品記錄
{
  "category_field": [
    {
      "sid": "9dd9272b-e7e5-40d5-8a6d-d2403d1e45c2",  // 用於查詢
      "name": "實木衣櫃"  // 用於顯示
    }
  ]
}

// 如果需要取得分類的圖示、描述等其他資訊,必須使用 sid 查詢
// sid === 目標表中的 rowid
```

**使用場景**:
- 只需要顯示名稱 → 直接使用 `name`
- 需要顯示其他欄位(圖片、價格、描述等) → 使用 `sid` 查詢目標表

---

**Q2: 關聯欄位建立後能修改dataSource嗎?**

❌ 不能。dataSource一旦設定不可修改,只能刪除欄位重建。

---

**Q3: 如何實現級聯刪除?**

透過工作流實現。當源記錄刪除時,觸發工作流刪除關聯記錄。

---

**Q4: 關聯欄位能跨應用嗎?**

✅ 可以。只要有目標工作表的ID,即使在不同應用也能關聯。

---

**Q5: 雙向關聯的反向欄位名稱可以自訂嗎?**

❌ 不能。系統自動生成,格式為"關聯{源表名}"。

---

**Q6: 關聯記錄被刪除後,關聯欄位會怎樣?**

關聯欄位會自動清空該關聯關係,不會報錯。

---

**Q7: 為什麼查詢關聯記錄要用 `rowid` 欄位而不是其他欄位?**

因為 `rowid` 是 niio 系統欄位,每條記錄都有唯一的 `rowid`。關聯欄位回傳的 `sid` 就是目標記錄的 `rowid`。

**示例**:
```javascript
// 關聯欄位回傳的 sid
const categoryId = product.category[0].sid;  // "9dd9272b-..."

// 查詢目標表時,使用 rowid 欄位匹配
{
  "filter": {
    "type": "condition",
    "field": "rowid",  // 必須用 rowid
    "operator": "in",
    "value": [categoryId]  // 傳入 sid
  }
}
```

---

## 七、常見陷阱與解決方案

### 7.1 選項欄位陷阱 ⭐⭐⭐

**問題**: 篩選單選/多選欄位時回傳空結果

**錯誤示例**:
```json
{
  "field": "customer_type",
  "operator": "eq",
  "value": ["成交客戶"]  // ❌ 使用了顯示文字
}
```

**正確做法**:
```json
{
  "field": "customer_type",
  "operator": "eq",
  "value": ["74c7b607-864d-4cc4-b401-28acba2636e9"]  // ✅ 使用選項key
}
```

**解決方案**:
1. 初始化時查詢工作表結構,快取選項對映
2. 或先查詢一條記錄,從回傳資料取得key
3. 建立 value → key 的對映表

---

### 7.2 數值欄位陷阱

**問題**: 數值篩選無結果或報錯

**錯誤示例**:
```json
{
  "field": "annual_budget",
  "operator": "gt",
  "value": [1000000]  // ❌ 數字型別
}
```

**正確做法**:
```json
{
  "field": "annual_budget",
  "operator": "gt",
  "value": ["1000000"]  // ✅ 字串陣列
}
```

**記憶口訣**: 篩選條件的value永遠是字串陣列

---

### 7.3 關聯欄位陷阱 ⭐⭐⭐

**問題1**: 使用錯誤的運算子篩選關聯欄位

**錯誤示例**:
```json
{
  "field": "related_customer",
  "operator": "belongsto",  // ❌ V3 API 不支援 belongsto；關聯欄位應用 in/eq
  "value": ["customer-id"]
}
```

**正確做法**:
```json
{
  "field": "related_customer",
  "operator": "in",  // ✅ 使用 in 或 eq
  "value": ["customer-id"]  // 傳入關聯記錄的 rowid 陣列
}
```

**關聯欄位支援的運算子**:
- `in`: 在指定關聯記錄中（值為 rowid 陣列）
- `eq`: 等於指定關聯記錄（單值）
- `isempty`: 關聯欄位為空
- `isnotempty`: 關聯欄位不為空

---

**問題2**: 混淆 `sid` 和欄位名

**錯誤示例**:
```javascript
// 錯誤:嘗試從關聯欄位直接取得目標表的其他欄位
const categoryIcon = product.category[0].icon;  // ❌ undefined!
```

**正確理解**:
```javascript
// 關聯欄位只回傳 sid 和 name
const category = product.category[0];
console.log(category);
// {
//   "sid": "9dd9272b-...",  // 關聯記錄ID
//   "name": "實木衣櫃"      // 標題欄位值
// }

// 如果需要 icon 等其他欄位,必須查詢目標表
const categoryData = await getRows('category-worksheet-id', {
  filter: {
    type: 'condition',
    field: 'rowid',
    operator: 'in',
    value: [category.sid]  // 使用 sid 查詢
  }
});

console.log(categoryData.rows[0].icon);  // ✅ 正確取得
```

---

**問題3**: 在清單頁逐個查詢關聯資料 (N+1 問題)

**錯誤示例**:
```javascript
// ❌ 效能災難:100個產品 = 1 + 100 = 101次請求
const products = await getProductList();  // 1次請求

for (const product of products) {
  const categoryId = product.category[0].sid;
  const category = await getCategoryById(categoryId);  // 100次請求!
  console.log(category.name);
}
```

**正確做法**: 批次查詢 (參見 Section 6.5.4)
```javascript
// ✅ 效能最佳化:100個產品 = 1 + 1 = 2次請求
const products = await getProductList();  // 1次請求

// 收集所有分類ID
const categoryIds = new Set();
products.forEach(p => {
  if (p.category && p.category.length > 0) {
    categoryIds.add(p.category[0].sid);
  }
});

// 批次查詢所有分類
const categories = await getRows('category-worksheet-id', {
  filter: {
    type: 'condition',
    field: 'rowid',
    operator: 'in',
    value: Array.from(categoryIds)
  }
});  // 1次請求

// 建立對映
const categoryMap = {};
categories.rows.forEach(cat => {
  categoryMap[cat.rowid] = cat;
});

// O(1) 查詢
products.forEach(p => {
  const category = categoryMap[p.category[0].sid];
  console.log(category.name, category.icon);
});
```

---

### 7.4 附件欄位陷阱

**問題**: 附件上傳後立即讀取回傳空陣列

**原因**: 附件上傳是非同步處理,需要5-10秒

**解決方案**:
```javascript
// 上傳附件
await updateRecord({
  fields: [{
    id: "attachments",
    type: "0",
    value: [{name: "file.pdf", url: "https://..."}]
  }]
});

// 等待5秒
await sleep(5000);

// 再讀取記錄
const record = await getRecord(rowId);
console.log(record.attachments);  // 現在有資料了
```

**建議**: 使用niio內部URL,外部URL可能有跨域限制

---

### 7.5 日期欄位陷阱

**問題**: 日期寫入時帶時間,讀取時只回傳日期

**原因**: Date欄位的subType決定回傳精度

**示例**:
```json
// 建立欄位
{
  "type": "Date",
  "subType": "3"  // 年月日
}

// 寫入
{
  "value": "2025-01-11 14:30:00"
}

// 讀取回傳
{
  "date_field": "2025-01-11"  // 時間被截斷
}
```

**解決方案**: 如需保留時間,使用 `subType: "6"` (年月日時分秒)

---

### 7.6 Filter巢狀陷阱

**問題**: 過度巢狀導致查詢失敗

**錯誤示例**:
```json
{
  "type": "group",
  "children": [
    {
      "type": "group",
      "children": [
        {
          "type": "group",  // ❌ 第三層巢狀
          "children": [...]
        }
      ]
    }
  ]
}
```

**限制**: 最多兩層巢狀 (group → group → condition)

**解決方案**: 重新設計查詢邏輯,合併條件

---

### 7.7 成員欄位陷阱

**問題**: 使用姓名查詢成員欄位失敗

**錯誤示例**:
```json
{
  "field": "owner",
  "operator": "eq",
  "value": ["張三"]  // ❌ 姓名無效
}
```

**正確做法**:
```bash
# Step 1: 透過姓名查詢使用者ID
POST /v3/users/lookup
{"name": "張三"}

# 回傳: {"accountId": "user-123"}

# Step 2: 使用使用者ID篩選
{
  "field": "owner",
  "operator": "eq",
  "value": ["user-123"]  // ✅ 使用者ID
}
```

---

### 7.8 批次操作陷阱

**問題**: 批次更新時誤覆蓋不同記錄

**場景**: 想給不同客戶設定不同評級

**錯誤做法**:
```json
{
  "rowIds": ["id1", "id2", "id3"],
  "fields": [
    {"id": "rating", "value": "5"}  // ❌ 所有記錄都變成5星
  ]
}
```

**解決方案**: 使用單條更新或批次建立時分別指定

---

## 八、效能最佳化建議

### 8.1 查詢最佳化

1. **合理使用分頁**: pageSize不要超過1000
2. **指定回傳欄位**: 使用fields參數,只回傳需要的欄位
3. **使用欄位ID**: 比別名查詢效能更好
4. **避免過度巢狀**: Filter巢狀控制在2層以內
5. **善用檢視**: 複雜篩選可先建立檢視,再查詢檢視

---

### 8.2 批次操作最佳化

1. **批次建立**: 一次最多100條
2. **批次更新**: 一次最多100條
3. **非同步處理**: 大批次操作使用佇列非同步處理

---

### 8.3 關聯欄位最佳化

1. **減少巢狀查詢**: 使用 get_record_relations API 一次取得
2. **快取關聯資料**: 頻繁訪問的關聯資料可快取
3. **控制showFields**: 只顯示必要欄位,減少資料量

---

## 九、最佳實踐總結

### 9.1 初始化階段

**必做事項**:
1. 查詢所有工作表結構
2. 快取所有選項欄位的key-value對映
3. 快取工作表ID和欄位ID
4. 建立使用者姓名→ID對映

**示例程式碼邏輯**:
```javascript
// 1. 取得工作表結構
const structure = await getWorksheetStructure(worksheetId);

// 2. 提取選項欄位對映
const optionMaps = {};
structure.fields.forEach(field => {
  if (field.type === 'SingleSelect' || field.type === 'MultipleSelect') {
    optionMaps[field.id] = {};
    field.options.forEach(opt => {
      optionMaps[field.id][opt.value] = opt.key;  // value → key
    });
  }
});

// 3. 使用時查詢key
const customerTypeKey = optionMaps['customer_type']['成交客戶'];
```

---

### 9.2 查詢階段

**建議**:
1. 優先使用欄位ID而不是別名
2. 選項欄位必須用key,提前轉換
3. 數值欄位value用字串
4. 關聯欄位用 in 或 eq 運算子（value 為 rowid 陣列）
5. 合理設定pageSize(建議100-500)

---

### 9.3 寫入階段

**檢查清單**:
- [ ] 選項欄位value是陣列格式
- [ ] 選項欄位傳的是key不是value
- [ ] 數值欄位傳數字型別
- [ ] 關聯欄位傳的是rowid
- [ ] 成員欄位傳的是accountId
- [ ] 附件欄位設定了type參數

---

### 9.4 錯誤處理

**常見錯誤碼**:
- `error_code: 1` - 成功
- `error_code: -1` - 失敗,檢視error_msg
- `error_code: 4` - 權限不足
- `error_code: 10` - 參數錯誤

**建議**: 所有API呼叫都要檢查error_code和success

---

## 十、完整示例:建置CRM應用

### 10.1 建立工作表

```bash
# 1. 建立客戶表
POST /v3/app/worksheets
{
  "name": "客戶資訊表",
  "fields": [
    {"name": "客戶名稱", "type": "Text", "isTitle": true},
    {"name": "客戶型別", "type": "SingleSelect", "options": [...]},
    {"name": "年度預算", "type": "Number", "precision": 2}
  ]
}

# 2. 建立機會表(關聯客戶)
POST /v3/app/worksheets
{
  "name": "銷售機會表",
  "fields": [
    {"name": "機會名稱", "type": "Text", "isTitle": true},
    {
      "name": "關聯客戶",
      "type": "Relation",
      "subType": "1",
      "dataSource": "{customer_table_id}"
    }
  ]
}
```

---

### 10.2 建立資料

```bash
# 1. 建立客戶
POST /v3/app/worksheets/{customer_table_id}/rows
{
  "fields": [
    {"id": "customer_name", "value": "niio科技"},
    {"id": "customer_type", "value": ["{成交客戶key}"]},
    {"id": "annual_budget", "value": 1000000}
  ]
}

# 2. 建立機會(關聯客戶)
POST /v3/app/worksheets/{opportunity_table_id}/rows
{
  "fields": [
    {"id": "opportunity_name", "value": "年度續費"},
    {"id": "related_customer", "value": ["{customer_rowid}"]}
  ]
}
```

---

### 10.3 查詢分析

```bash
# 1. 查詢重點客戶
POST /v3/app/worksheets/{customer_table_id}/rows/list
{
  "filter": {
    "type": "group",
    "logic": "AND",
    "children": [
      {"type": "condition", "field": "customer_type", "operator": "eq", "value": ["{成交key}"]},
      {"type": "condition", "field": "annual_budget", "operator": "gte", "value": ["500000"]}
    ]
  }
}

# 2. 按行業統計客戶
POST /v3/app/worksheets/{customer_table_id}/rows/pivot
{
  "rows": [{"field": "industry"}],
  "values": [
    {"field": "rowid", "aggregation": "COUNT"},
    {"field": "annual_budget", "aggregation": "SUM"}
  ]
}
```

---

## 附錄A:欄位型別速查表

| 型別 | type值 | 寫入格式 | 讀取格式 | 關鍵參數 |
|-----|--------|---------|---------|---------|
| 文字 | Text | 字串 | 字串 | - |
| 數值 | Number | 數字 | 字串 | precision |
| 單選 | SingleSelect | 陣列[key] | 物件陣列 | options |
| 多選 | MultipleSelect | 陣列[key...] | 物件陣列 | options |
| 日期 | Date | 字串 | 字串 | subType |
| 時間 | Time | 字串 | 字串 | subType |
| 成員 | Collaborator | 陣列[id] | 物件/陣列 | subType |
| 關聯 | Relation | 陣列[rowid] | 物件/陣列 | dataSource, subType |
| 附件 | Attachment | 物件陣列 | 物件陣列 | - |
| 等級 | Rating | 字串 | 字串 | max |

---

## 附錄B:運算子速查表

| 運算子 | 適用欄位 | value格式 | 說明 |
|-------|---------|----------|------|
| eq | 所有 | ["值"] | 等於 |
| ne | 所有 | ["值"] | 不等於 |
| contains | Text, Multi | ["值"] | 包含 |
| startswith | Text | ["值"] | 開頭是 |
| gt/gte/lt/lte | Number, Date | ["值"] | 比較 |
| between | Number, Date | ["最小", "最大"] | 範圍 |
| isempty | 所有 | 無 | 為空 |
| in / eq | Relation | ["rowid"...] | 關聯（值為 rowid） |
| in / eq / notin | 部門(Department) | ["部門ID"...] | 部門篩選（V3 API 無 belongsto） |

---

## 附錄C:錯誤排查清單

**篩選無結果**:
- [ ] 選項欄位是否用了key而不是value?
- [ ] 數值欄位value是否用了字串?
- [ ] 關聯欄位是否用了 in/eq + rowid?
- [ ] Filter巢狀是否超過2層?
- [ ] 欄位ID是否正確?

**建立/更新失敗**:
- [ ] 必填欄位是否都提供了?
- [ ] 關聯欄位的dataSource是否存在?
- [ ] 選項欄位的key是否有效?
- [ ] 成員欄位的accountId是否有效?
- [ ] 數值欄位是否超出範圍?

**資料異常**:
- [ ] 附件是否等待了5-10秒?
- [ ] 日期精度subType是否正確?
- [ ] 關聯記錄是否已刪除?

---

**文件版本**: v1.0
**生成時間**: 2026-01-11
**基於**: niio API V3
**測試驗證**: 完整CRM應用場景測試
