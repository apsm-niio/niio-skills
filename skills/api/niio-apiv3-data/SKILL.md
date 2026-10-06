---
name: niio-apiv3-data
description: 使用niio V3 介面建置頁面和操作資料的專業技能。立即觸發條件：使用者提到"niio V3"、"niio API"、"API 呼叫"、"資料 API"、"Appkey"、"Sign"、"介面身分驗證與授權"、"PAT"、"OAuth"、"Bearer"、"Filter 篩選"、"查詢資料"、"建立記錄"。提供完整的 API 使用指南：身分驗證與授權設定、API 呼叫、篩選器使用、資料操作等。如果使用者已設定 niio MCP，AI 應該自動從 MCP 設定中提取身分驗證與授權金鑰。
license: MIT
---
> **部署設定**：範例 API 使用 `https://niiodemo.apsm.com.tw`；其他部署須替換為該環境網址與憑證。API、MCP 與網站網址必須使用本次選定部署環境的已確認設定，三者可能不同，不得只依 MCP 網址推測 API 或網站位置。下方 `.example.invalid` 網址只是不可連線的佔位範例，執行前必須替換；未確認網址時先詢問，不得向佔位網址傳送憑證。圖片與附件只能使用使用者提供或已授權的素材網址。

> **對外表達規範**：對使用者的說明、提示與成果摘要，統一使用 niio 品牌及台灣繁體中文。執行所需的技術名稱、套件、命令、API 參數與路徑請保留；只在操作或除錯所需的程式碼中呈現，勿將它們用作產品標題或品牌名稱。


# niio V3 API 使用技能

此技能提供使用niio V3 介面建置頁面、即時取得資料和操作資料的完整指南。

## Overview

niio 是一個超級應用平台,透過這個基座可以建置很多應用。透過 niio V3 介面,您可以:

1. **在自訂檢視外掛中**呼叫 V3 介面操作資料
2. **在獨立前端頁面中**使用 V3 介面編排業務邏輯
3. **即時取得和操作**niio應用中的資料

**核心能力:**
- ✅ 完整的 API 使用工作流（從零建置應用到資料操作）
- ✅ 詳細的欄位型別處理規範
- ✅ Filter 篩選器完整語法
- ✅ 關聯欄位深度查詢指南
- ✅ 常見陷阱和解決方案
- ✅ 效能最佳化最佳實踐

**詳細文件:** 參考 `references/niio-api-usage-guide.md` 取得完整的 API 使用規範

---

## 快速開始

### 1. 取得 API 憑證

**方法一: 從 MCP 設定中提取（推薦）**

如果使用者已經設定了 niio 應用執行 MCP，AI 助手應該**自動從 MCP 設定中提取身分驗證與授權金鑰**，而不是讓使用者手動輸入。

#### 自動化提取步驟

1. **讀取已設定的 niio MCP 設定檔案**（以編輯器/客戶端的 MCP 設定為準，例如其全域 `settings.json`）
   - **macOS**: `~/Library/Application Support/<編輯器>/User/settings.json`
   - **Windows**: `%APPDATA%\<編輯器>\User\settings.json`
   - **Linux**: `~/.config/<編輯器>/User/settings.json`

2. **查詢 MCP 設定**
   - 使用已確認的 MCP 連線名稱與網址，不依品牌網域判斷。
   - 常見命名：AppKey 身分驗證與授權多為 `niio-mcp-應用名`；個人身分驗證與授權多為 `niio_personal_mcp`

3. **識別身分驗證與授權型別並解析參數**

   niio MCP 設定有兩種身分驗證與授權格式，需分別處理：

   **格式一 · AppKey + Sign**（金鑰寫在 `url` 查詢參數裡）
   ```json
   {
     "mcpServers": {
       "niio-mcp-應用名": {
         "url": "https://niiodemo.apsm.com.tw/mcp?HAP-Appkey=你的Appkey&HAP-Sign=你的Sign"
       }
     }
   }
   ```

   **格式二 · PAT / OAuth**（令牌寫在 `headers.Authorization` 裡）
   ```json
   {
     "mcpServers": {
       "niio_personal_mcp": {
         "url": "https://niiodemo.apsm.com.tw/mcp",
         "headers": {
           "Authorization": "Bearer pat_XXX"
         }
       }
     }
   }
   ```

4. **提取身分驗證與授權資訊**
   - 格式一：從 `url` 查詢參數取 `HAP-Appkey`、`HAP-Sign`（參數可能經 URL 編碼，需正確解碼），請求時放入同名請求頭。
   - 格式二：從 `headers.Authorization` 取整串 `Bearer …`，請求時原樣放入 `Authorization` 頭；如介面要求，另帶 `HAP-Appid`（應用 ID）。
   - 判定規則：`url` 含 `HAP-Appkey` → 走格式一；否則看 `headers.Authorization` → 走格式二。

#### 程式碼示例（AI 助手操作）

```javascript
// 1. 讀取已設定的 niio MCP 設定檔案（路徑取決於所用編輯器/客戶端，下方以其全域 settings.json 為例）
const editorDir = 'YourEditor'; // 替換為實際編輯器/客戶端目錄名
const settingsPath = process.platform === 'darwin' 
  ? `${process.env.HOME}/Library/Application Support/${editorDir}/User/settings.json`
  : process.platform === 'win32'
  ? `${process.env.APPDATA}/${editorDir}/User/settings.json`
  : `${process.env.HOME}/.config/${editorDir}/User/settings.json`;

const settings = JSON.parse(fs.readFileSync(settingsPath, 'utf8'));

// 依使用者指定的連線名稱取得 MCP 設定
const mcpServers = settings.mcpServers || {};
// selectedMcpName 必須由使用者選定，不能靠品牌網域猜測或任取第一筆。
const selectedMcpName = process.env.NIIO_MCP_SERVER_NAME;
if (!selectedMcpName || !mcpServers[selectedMcpName]?.url) {
  throw new Error('請先指定本次要使用的 MCP 連線名稱');
}
const hapMcpConfig = [selectedMcpName, mcpServers[selectedMcpName]];

if (hapMcpConfig) {
  const [, config] = hapMcpConfig;
  const url = new URL(config.url);

  // 3. 識別身分驗證與授權型別並提取
  let auth;
  if (url.searchParams.get('HAP-Appkey')) {
    // 格式一：AppKey + Sign
    auth = {
      type: 'appkey',
      headers: {
        'HAP-Appkey': url.searchParams.get('HAP-Appkey'),
        'HAP-Sign': url.searchParams.get('HAP-Sign'),
      },
    };
  } else if (config.headers?.Authorization) {
    // 格式二：PAT / OAuth（Bearer Token）
    auth = {
      type: 'bearer',
      headers: {
        'Authorization': config.headers.Authorization, // 原樣使用 "Bearer ..."
        // 'HAP-Appid': '應用ID',  // 應用級介面必填，按需補充
      },
    };
  }

  // 4. 將 auth.headers 合併進 API 請求頭即可
  console.log('已取得所選環境的認證設定'); // 不輸出憑證
}
```

#### 實際操作流程

當使用者需要呼叫 niio API 時，AI 應該：

1. **檢查是否已設定 MCP**
   - 讀取已設定的 niio MCP 設定
   - 查詢 `niio-mcp-*` 設定

2. **提取身分驗證與授權資訊**
   - 找到設定後，按格式自動提取：URL 參數裡的 `HAP-Appkey`/`HAP-Sign`，或 `headers.Authorization` 裡的 `Bearer` 令牌
   - 如果找到多個 MCP 設定，詢問使用者使用哪個應用

3. **使用提取的身分驗證與授權**
   - 在 API 請求頭中帶上提取到的身分驗證與授權頭（`HAP-Appkey`+`HAP-Sign`，或 `Authorization: Bearer …`，PAT/OAuth 按需加 `HAP-Appid`）
   - 如果提取失敗，提示使用者手動提供或檢查 MCP 設定

#### 注意事項

- ✅ **優先使用 MCP 設定**: 如果使用者已設定 MCP，優先從設定中提取
- ✅ **URL 解碼**: 注意 URL 參數可能經過編碼，需要正確解碼
- ✅ **多個應用**: 如果設定了多個 niio MCP，詢問使用者使用哪個應用
- ⚠️ **設定不存在**: 如果未找到 MCP 設定，提示使用者先設定 MCP 或手動提供金鑰
- ⚠️ **權限問題**: 如果無法讀取設定檔案，提示使用者檢查檔案權限

**方法二: 手動取得**

如果使用者未設定 MCP 或需要手動提供：

1. 登入niio → 應用 → 設定 → API 金鑰
2. 複製 Appkey 和 Sign
3. 或提供 MCP 設定資訊，讓 AI 自動提取

### 2. 設定請求頭（身分驗證與授權）

身分驗證與授權用於驗證"你是誰、有沒有權限"，憑證統一放在請求 **Header** 中，每個請求都必須攜帶。V3 支援三種身分驗證與授權方式：

| 方式 | Header 參數 | 操作身份 | 有效期 | 適用場景 |
| --- | --- | --- | --- | --- |
| **AppKey + Sign** | `HAP-Appkey`、`HAP-Sign` | 應用管理員 | 長期 | 伺服器端整合 |
| **PAT** | `Authorization: Bearer {access_token}`、`HAP-Appid`（部分介面必填） | 個人 | 可設定 | 個人指令碼 / 工具 |
| **OAuth 2.0** | `Authorization: Bearer {access_token}`、`HAP-Appid`（部分介面必填） | 被授權使用者 | 短期，自動重新整理 | 第三方應用整合 |

**方式一：AppKey + Sign（應用金鑰，最常用）**

由管理員建立，以應用管理員身份訪問資料。

```javascript
const headers = {
  'Content-Type': 'application/json',
  'HAP-Appkey': '你的Appkey',
  'HAP-Sign': '你的Sign'
};
```

> ⚠️ 請求頭名是 `HAP-Appkey` 和 `HAP-Sign`（**不是** `AppKey` 和 `Sign`）。

**方式二：PAT（個人訪問憑證）**

自行建立，以個人身份操作，可設定有效期和權限範圍。

```javascript
const headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer 你的access_token',
  'HAP-Appid': '應用ID'   // 應用級介面必填
};
```

**方式三：OAuth 2.0（第三方授權）**

使用者透過 OAuth 整合完成授權，短期有效、支援自動重新整理。請求頭同 PAT：

```javascript
const headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer 你的access_token',
  'HAP-Appid': '應用ID'   // 應用級介面必填
};
```

**PAT / OAuth 2.0 的附加參數：**
- `HAP-Appid`（Header）：標識來源應用，值為應用 ID，**應用級介面必填**。
- `orgId`（Query）：標識來源組織，值為組織 ID，**組織級介面必填**（如取得應用清單、建立應用）。

> 三種方式按場景選用：伺服器端整合用 AppKey + Sign；個人指令碼/工具用 PAT；第三方應用整合用 OAuth 2.0。

### 3. 取得 API 文件

**使用 Apifox MCP Server（推薦）:**

```json
{
  "應用 API - API 文件": {
    "command": "npx",
    "args": [
      "-y",
      "apifox-mcp-server@latest",
      "--site-id=5442569"
    ]
  }
}
```

**線上文件資源:**
- API 整體介紹（請參閱此技能隨附文件或部署管理者提供的說明）
- 欄位型別對照表（請參閱此技能隨附文件或部署管理者提供的說明）
- 篩選器使用指南（請參閱此技能隨附文件或部署管理者提供的說明）
- 錯誤碼說明（請參閱此技能隨附文件或部署管理者提供的說明）

---

## 核心工作流程

### 階段一: 準備工作

**Step 1: 取得 API 憑證**
- **優先方式**: 從已設定的 niio MCP 設定中自動提取 Appkey 和 Sign（如果使用者已設定）
- **備選方式**: 從 niio 後臺手動取得或讓使用者提供

**Step 2: 設定 API 請求頭**
- 使用提取或提供的 Appkey 和 Sign 設定請求頭
- 設定 `HAP-Appkey` 和 `HAP-Sign` 請求頭

### 階段二: 建立應用結構

**Step 3: 取得應用資訊（可選）**
```javascript
GET /v3/app/info
```

**Step 4: 建立工作表**
```javascript
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
    }
  ]
}
```

**詳細規範:** 參考 `references/niio-api-usage-guide.md` 第 1 節

### 階段三: 填充資料

**Step 5: 準備選項欄位對映**
- 對於單選/多選欄位,需要先取得選項的 key（UUID）
- 查詢工作表結構取得 options 清單

**Step 6: 建立記錄**
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
      "value": ["74c7b607-864d-4cc4-b401-28acba2636e9"]  // ⚠️ 使用選項key
    }
  ],
  "triggerWorkflow": true
}
```

**關鍵點:**
- ⚠️ 選項欄位必須用 key,不能用顯示文字
- ⚠️ 選項欄位即使單選也要用陣列格式
- ✅ 數值欄位寫入時傳數字,讀取時回傳字串

**詳細規範:** 參考 `references/niio-api-usage-guide.md` 第 3 節

### 階段四: 查詢和分析資料

**Step 7: 查詢記錄清單**
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
        "value": ["74c7b607-864d-4cc4-b401-28acba2636e9"]  // 使用key
      }
    ]
  },
  "sorts": [{
    "field": "annual_budget",
    "isAsc": false
  }],
  "pageIndex": 1,
  "pageSize": 20
}
```

**詳細規範:** 參考 `references/niio-api-usage-guide.md` 第 4 節

---

## Filter 篩選器規範 ⭐重點

### Filter 物件結構

**基礎結構:**
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

**規則:**
1. 頂層必須是 `group` 型別
2. 最多兩層巢狀: group → group → condition
3. 同一 group 的 children 必須型別一致
4. group 必須指定 `logic` (AND/OR)
5. condition 必須指定 `field`, `operator`

### 運算子完整清單

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

### 篩選示例

**示例1: 單選欄位篩選（⚠️ 必須使用 key）**
```javascript
{
  "type": "group",
  "logic": "AND",
  "children": [{
    "type": "condition",
    "field": "customer_type",
    "operator": "eq",
    "value": ["74c7b607-864d-4cc4-b401-28acba2636e9"]  // ✅ 使用key
  }]
}

// ❌ 錯誤: value: ["成交客戶"]  // 不能用顯示文字!
```

**示例2: 數值範圍篩選（⚠️ value 必須是字串陣列）**
```javascript
{
  "type": "condition",
  "field": "annual_budget",
  "operator": "between",
  "value": ["500000", "2000000"]  // ✅ 字串陣列
}

// ❌ 錯誤: value: [500000, 2000000]  // 不能用數字!
```

**示例3: 關聯欄位篩選（⚠️ 用 in 或 eq）**
```javascript
{
  "type": "condition",
  "field": "related_customer",
  "operator": "in",  // ✅ 關聯欄位用 in（多值）或 eq（單值）
  "value": ["customer-row-id"]  // 傳入關聯記錄的 rowid 陣列
}

// ❌ 錯誤: operator: "belongsto"  // V3 API 無 belongsto 運算子，關聯欄位應用 in/eq + rowid
```

**詳細規範:** 參考 `references/niio-api-usage-guide.md` 第 4 節

---

## 欄位型別處理規範

### 欄位型別 / Code / 篩選運算子對照表（API 權威）⭐

> 這是欄位 **Code** 與各欄位 **支援的篩選運算子** 的權威依據。要點：
> - **V3 API 沒有 `belongsto` 運算子**——部門(Department)、關聯(Relation) 等欄位一律用本表運算子（如 `in`、`eq`、`notin`）。
> - `-` 表示不支援該能力；篩選寫法只能用對應欄位「支援的篩選運算子」列裡的值。

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

### 關鍵欄位型別處理

#### 1. 選項欄位（SingleSelect/MultipleSelect）⭐⭐⭐

**寫入:** 必須傳選項 key 的陣列
```javascript
{
  "id": "customer_type",
  "value": ["74c7b607-864d-4cc4-b401-28acba2636e9"]  // 選項key
}
```

**讀取:** 回傳包含 key 和 value 的物件陣列
```javascript
{
  "customer_type": [
    {
      "key": "74c7b607-864d-4cc4-b401-28acba2636e9",
      "value": "成交客戶"
    }
  ]
}
```

**⚠️ 關鍵點:**
- 即使是單選,也要用陣列 `["key"]`
- 不能傳顯示文字 `["成交客戶"]`,必須用 key
- 篩選時必須使用 key,不能使用顯示文字

#### 2. 附件欄位（Attachment）⭐

**寫入:** 支援 URL 和 base64
```javascript
{
  "id": "attachments",
  "type": "0",  // 0=覆蓋, 1=追加
  "value": [{
    "name": "產品宣傳冊.pdf",
    "url": "https://example.com/brochure.pdf"
  }]
}
```

**讀取:** 回傳附件物件陣列
```javascript
{
  "attachments": [{
    "file_id": "...",
    "file_name": "...",
    "downloadUrl": "https://...",  // ⚠️ 使用 downloadUrl
    "file_size": 2048576
  }]
}
```

**⚠️ 重要提示:**
- 附件上傳是非同步處理,通常需要 5-10 秒
- API 回傳成功不代表附件已上傳完成
- 使用 `downloadUrl` 而非 `url`

#### 3. 關聯欄位（Relation）⭐⭐⭐

**寫入:** 傳記錄 ID 陣列
```javascript
{
  "id": "related_customer",
  "value": ["945e6503-3823-4e91-9d84-a53f8bdd6fc5"]  // 記錄rowid
}
```

**讀取:** 回傳物件陣列（只包含 sid 和 name）
```javascript
{
  "related_customer": [{
    "sid": "945e6503-3823-4e91-9d84-a53f8bdd6fc5",
    "name": "niio科技有限公司"
  }]
}
```

**取得完整關聯資料:**
```javascript
// 方法1: 使用專用 API
GET /v3/app/worksheets/{worksheet_id}/rows/{row_id}/relations/{field_id}

// 方法2: 使用 sid 查詢目標表
POST /v3/app/worksheets/{target_worksheet_id}/rows/list
{
  "filter": {
    "type": "group",
    "logic": "AND",
    "children": [{
      "type": "condition",
      "field": "rowid",  // ⚠️ 使用系統欄位 rowid
      "operator": "in",
      "value": ["sid1", "sid2"]  // 傳入關聯記錄的 sid
    }]
  }
}
```

**詳細規範:** 參考 `references/niio-api-usage-guide.md` 第 6 節

#### 4. 成員欄位（Collaborator）

**寫入:** 傳使用者 ID 陣列
```javascript
{
  "id": "owner",
  "value": ["user-account-id-123"]  // 使用者ID,不是使用者名稱
}
```

**取得使用者ID:**
```javascript
POST /v3/users/lookup
{
  "name": "張三"  // 精確匹配姓名
}
```

#### 5. 數值欄位（Number）

**寫入:** 傳數字型別
```javascript
{
  "id": "annual_budget",
  "value": 1000000.50
}
```

**讀取:** 回傳字串
```javascript
{
  "annual_budget": "1000000.50"
}
```

**⚠️ 注意:** 寫入數字,讀取字串

**詳細規範:** 參考 `references/niio-api-usage-guide.md` 第 2、3 節

---

## triggerWorkflow 參數詳解 ⭐重要

`triggerWorkflow` 參數控制是否在資料操作時觸發工作表相關的工作流。

**適用範圍:**
- ✅ 建立記錄
- ✅ 批次建立
- ✅ 更新記錄
- ✅ 批次更新
- ✅ 刪除記錄
- ✅ 批次刪除

**參數說明:**

| 參數值 | 說明 | 預設值 | 使用場景 |
|-------|------|--------|---------|
| `true` | 觸發工作流 | ✅ 是 | 正常業務操作,需要執行自動化流程 |
| `false` | 不觸發工作流 | ❌ 否 | 資料遷移、批次初始化、測試資料 |

**✅ 應該設定為 `true` 的場景:**
- 正常業務操作（使用者提交表單、更新狀態等）
- 需要自動化處理的操作

**❌ 應該設定為 `false` 的場景:**
- 資料遷移和匯入
- 批次資料初始化
- 定時同步任務
- 測試和除錯

**效能影響:**
- `triggerWorkflow: false` - API 響應快,通常 < 500ms
- `triggerWorkflow: true` - 需要等待工作流執行,可能需要 1-5 秒

**詳細說明:** 參考 `references/niio-api-usage-guide.md` 第 3.2 節

---

## 常見陷阱與解決方案 ⭐⭐⭐

### 陷阱1: 選項欄位篩選使用顯示文字

**問題:** 篩選單選/多選欄位時回傳空結果

**錯誤示例:**
```javascript
{
  "field": "customer_type",
  "operator": "eq",
  "value": ["成交客戶"]  // ❌ 使用了顯示文字
}
```

**正確做法:**
```javascript
{
  "field": "customer_type",
  "operator": "eq",
  "value": ["74c7b607-864d-4cc4-b401-28acba2636e9"]  // ✅ 使用選項key
}
```

**解決方案:**
1. 初始化時查詢工作表結構,快取選項對映
2. 或先查詢一條記錄,從回傳資料取得 key
3. 建立 value → key 的對映表

### 陷阱2: 數值欄位篩選使用數字型別

**問題:** 數值篩選無結果或報錯

**錯誤示例:**
```javascript
{
  "field": "annual_budget",
  "operator": "gt",
  "value": [1000000]  // ❌ 數字型別
}
```

**正確做法:**
```javascript
{
  "field": "annual_budget",
  "operator": "gt",
  "value": ["1000000"]  // ✅ 字串陣列
}
```

**記憶口訣:** 篩選條件的 value 永遠是字串陣列

### 陷阱3: 關聯欄位使用錯誤的運算子

**問題:** 使用錯誤的運算子篩選關聯欄位

**錯誤示例:**
```javascript
{
  "field": "related_customer",
  "operator": "belongsto",  // ❌ V3 API 不支援 belongsto；關聯欄位應用 in/eq
  "value": ["customer-id"]
}
```

**正確做法:**
```javascript
{
  "field": "related_customer",
  "operator": "in",  // ✅ 關聯欄位用 in 或 eq
  "value": ["customer-row-id"]  // 傳入關聯記錄的 rowid 陣列
}
```

### 陷阱4: 關聯欄位 N+1 查詢問題

**問題:** 在清單頁逐個查詢關聯資料

**錯誤示例:**
```javascript
// ❌ 效能災難:100個產品 = 1 + 100 = 101次請求
const products = await getProductList();  // 1次請求

for (const product of products) {
  const categoryId = product.category[0].sid;
  const category = await getCategoryById(categoryId);  // 100次請求!
}
```

**正確做法:** 批次查詢
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
```

**詳細說明:** 參考 `references/niio-api-usage-guide.md` 第 7 節

---

## 效能最佳化建議

### 1. 查詢最佳化

- **合理使用分頁**: pageSize 不要超過 1000
- **指定回傳欄位**: 使用 fields 參數,只回傳需要的欄位
- **使用欄位ID**: 比別名查詢效能更好
- **避免過度巢狀**: Filter 巢狀控制在 2 層以內
- **善用檢視**: 複雜篩選可先建立檢視,再查詢檢視

### 2. 批次操作最佳化

- **批次建立**: 一次最多 100 條
- **批次更新**: 一次最多 100 條
- **包含關聯欄位**: 減少到每批 30-50 條
- **包含附件**: 建議單獨處理,不要批次
- **批次間延遲**: 每批間隔 1-2 秒

### 3. 關聯欄位最佳化

- **減少巢狀查詢**: 使用 get_record_relations API 一次取得
- **批次查詢**: 避免 N+1 查詢問題
- **快取關聯資料**: 頻繁訪問的關聯資料可快取
- **控制 showFields**: 只顯示必要欄位,減少資料量

**詳細說明:** 參考 `references/niio-api-usage-guide.md` 第 8 節

---

## 🤖 AI 助手使用指南

當使用者需要呼叫 niio V3 API 時，AI 助手應該遵循以下原則：

### 1. 自動提取身分驗證與授權金鑰

**優先順序順序：**

1. **優先從 MCP 設定提取**（推薦）
   - 讀取已設定的 niio MCP 設定
   - 查詢 `niio-mcp-*` 設定
   - 從 URL 中提取 `HAP-Appkey` 和 `HAP-Sign`
   - 如果找到多個設定，詢問使用者使用哪個應用

2. **使用者手動提供**
   - 如果未找到 MCP 設定，提示使用者提供 Appkey 和 Sign
   - 或引導使用者先設定 MCP

3. **引導設定 MCP**
   - 如果使用者有 MCP 設定資訊，幫助使用者設定到所用的編輯器/客戶端
   - 然後從設定中提取金鑰

### 2. 設定請求頭

提取到金鑰後，自動設定請求頭：

```javascript
const headers = {
  'Content-Type': 'application/json',
  'HAP-Appkey': extractedAppkey,  // 從 MCP 設定提取
  'HAP-Sign': extractedSign        // 從 MCP 設定提取
};
```

### 3. 處理多個應用

如果使用者設定了多個 niio MCP：

- **明確指定應用名**: 如果使用者提到具體應用名，使用對應的設定
- **詢問使用者**: 如果未指定，列出所有設定的應用，讓使用者選擇
- **預設使用**: 如果只有一個設定，直接使用

### 4. 錯誤處理

- **設定不存在**: 提示使用者先設定 MCP 或手動提供金鑰
- **URL 解析失敗**: 檢查 URL 格式是否正確
- **參數缺失**: 檢查 Appkey 和 Sign 是否都存在
- **權限問題**: 如果無法讀取設定檔案，提示使用者檢查檔案權限

### 5. 實際操作示例

**場景**: 使用者說"幫我呼叫 niio API 查詢資料"

**AI 操作流程**:
1. 讀取已設定的 niio MCP 設定檔案（路徑取決於所用編輯器/客戶端，如其全域 `settings.json`）
2. 查詢 `mcpServers` 中的 `niio-mcp-*` 設定
3. 如果找到設定，從 URL 中提取 Appkey 和 Sign
4. 如果找到多個設定，詢問使用者使用哪個應用
5. 使用提取的金鑰設定 API 請求頭
6. 執行 API 呼叫

**場景**: 使用者提供了 MCP 設定資訊

**AI 操作流程**:
1. 先幫助使用者將 MCP 設定新增到所用編輯器/客戶端的 MCP 設定檔案
2. 然後從設定中提取 Appkey 和 Sign
3. 使用提取的金鑰進行後續 API 呼叫

---

## 最佳實踐

### 1. 初始化階段

**必做事項:**
1. 查詢所有工作表結構
2. 快取所有選項欄位的 key-value 對映
3. 快取工作表 ID 和欄位 ID
4. 建立使用者姓名→ID 對映

**示例程式碼:**
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

### 2. 查詢階段

**建議:**
1. 優先使用欄位 ID 而不是別名
2. 選項欄位必須用 key,提前轉換
3. 數值欄位 value 用字串
4. 關聯欄位用 in 或 eq 運算子（value 為 rowid 陣列）
5. 合理設定 pageSize（建議 100-500）

### 3. 寫入階段

**檢查清單:**
- [ ] 選項欄位 value 是陣列格式
- [ ] 選項欄位傳的是 key 不是 value
- [ ] 數值欄位傳數字型別
- [ ] 關聯欄位傳的是 rowid
- [ ] 成員欄位傳的是 accountId
- [ ] 附件欄位設定了 type 參數

### 4. 錯誤處理

**常見錯誤碼:**
- `error_code: 1` - 成功
- `error_code: -1` - 失敗,檢視 error_msg
- `error_code: 4` - 權限不足
- `error_code: 10` - 參數錯誤

**建議:** 所有 API 呼叫都要檢查 error_code 和 success

**詳細說明:** 參考 `references/niio-api-usage-guide.md` 第 9 節

---

## 常用 API 端點速查

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
| 取得地區 | `POST /v3/regions` | search, id |

---

## 參考資源

### 核心文件

- **`references/niio-api-usage-guide.md`** - niio V3 API 使用規範完整指南
  - 快速開始 - API 使用流程
  - 建立工作表規範
  - 欄位型別參數詳解
  - 建立/更新記錄規範（triggerWorkflow 詳解）
  - 查詢篩選規範（Filter 物件結構、運算子清單）
  - 資料透視分析規範
  - 關聯欄位完整指南
  - 常見陷阱與解決方案
  - 效能最佳化建議
  - 最佳實踐總結

### 線上文件

- API 整體介紹（請參閱此技能隨附文件或部署管理者提供的說明）
- 欄位型別對照表（請參閱此技能隨附文件或部署管理者提供的說明）
- 篩選器使用指南（請參閱此技能隨附文件或部署管理者提供的說明）
- 錯誤碼說明（請參閱此技能隨附文件或部署管理者提供的說明）

### 相關技能

- **niio 前後端專案建置指南** - 使用 niio 作為資料庫建置獨立網站
- **niio 檢視外掛開發指南** - 開發 niio 自訂檢視外掛

---

## 關鍵概念速查

**欄位型別 (type):**
- 基礎: `Text`, `Number`, `Date`, `Time`
- 選擇: `SingleSelect`, `MultipleSelect`
- 關係: `Relation`, `Collaborator`, `Department`
- 其他: `Attachment`, `Rating`

**篩選運算子 (operator):**
- 比較: `eq`, `ne`, `gt`, `gte`, `lt`, `lte`
- 文字: `contains`, `startswith`, `endswith`
- 範圍: `between`, `in`
- 關聯(Relation): `in` / `eq`（值為 rowid 陣列）
- 部門(Department): `in` / `eq` / `notin` 等（詳見欄位型別對照表；V3 API 無 belongsto）
- 空值: `isempty`, `isnotempty`

**subType 參數:**
- Collaborator: `0`=單選, `1`=多選
- Relation: `1`=單條, `2`=多條
- Time: `1`=時:分, `6`=時:分:秒
- Date: `3`=年月日, `6`=年月日時分秒

---

## 錯誤排查清單

**篩選無結果:**
- [ ] 選項欄位是否用了 key 而不是 value?
- [ ] 數值欄位 value 是否用了字串?
- [ ] 關聯欄位是否用了 in/eq + rowid?
- [ ] Filter 巢狀是否超過 2 層?
- [ ] 欄位 ID 是否正確?

**建立/更新失敗:**
- [ ] 必填欄位是否都提供了?
- [ ] 關聯欄位的 dataSource 是否存在?
- [ ] 選項欄位的 key 是否有效?
- [ ] 成員欄位的 accountId 是否有效?
- [ ] 數值欄位是否超出範圍?

**資料異常:**
- [ ] 附件是否等待了 5-10 秒?
- [ ] 日期精度 subType 是否正確?
- [ ] 關聯記錄是否已刪除?

---

**技能版本**: v2.0  
**最後更新**: 2026-01-11  
**基於**: niio API V3  
**詳細規範**: 參考 `references/niio-api-usage-guide.md`
