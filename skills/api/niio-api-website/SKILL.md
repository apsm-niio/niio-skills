---
name: niio-api-website
description: 立即觸發條件：使用者提到"niio 建置網站"、"niio 前端專案"、"niio 作為資料庫"、"企業官網"、"官網"、"透過 niio 建置"、"用 niio 做網站"、"niio 網站"、"建置官網"、"前後端分離"、"內容管理系統"、"niio 前端"、"niio 官網"。提供完整的 niio + 前端專案建置指南，包括 niio 後臺設定、前端專案結構、API 整合和資料渲染。
license: MIT
---
> **部署設定**：範例 API 使用 `https://niiodemo.apsm.com.tw`；其他部署須替換為該環境網址與憑證。API、MCP 與網站網址必須使用本次選定部署環境的已確認設定，三者可能不同，不得只依 MCP 網址推測 API 或網站位置。下方 `.example.invalid` 網址只是不可連線的佔位範例，執行前必須替換；未確認網址時先詢問，不得向佔位網址傳送憑證。圖片與附件只能使用使用者提供或已授權的素材網址。

> **對外表達規範**：對使用者的說明、提示與成果摘要，統一使用 niio 品牌及台灣繁體中文。執行所需的技術名稱、套件、命令、API 參數與路徑請保留；只在操作或除錯所需的程式碼中呈現，勿將它們用作產品標題或品牌名稱。


# niio 前後端專案建置指南

## 觸發條件（MANDATORY）

<EXTREMELY_IMPORTANT>
**當使用者提到以下任何情況時，必須使用此技能：**

- ✅ "透過 niio 建置官網"
- ✅ "用 niio 做網站"
- ✅ "niio 前端專案"
- ✅ "niio 作為資料庫" + "網站"相關需求
- ✅ "企業官網" + "niio"相關需求
- ✅ "建置網站" + "niio"相關需求
- ✅ "官網" + "niio"相關需求
- ✅ "niio 網站"
- ✅ "niio 官網"
- ✅ "前後端分離" + "niio"相關需求
- ✅ "內容管理系統" + "niio"相關需求

**技能優先順序：**
- 如果使用者明確提到"niio" + "網站/官網/前端"，必須優先使用此技能
- 如果使用者提到"建置網站"但沒有提到技術棧，可以詢問是否使用 niio

**This is MANDATORY. No exceptions.**
</EXTREMELY_IMPORTANT>

---

## Overview

本技能提供使用**niio（高階應用平台）**作為後臺內容管理系統，建置完整前後端分離專案的完整工作流。適用於企業官網、內容管理網站、資料展示平台、表單收集系統等多種場景。

**核心能力：**
- ✅ niio 後臺資料結構設計與設定
- ✅ 前端專案架建置置（HTML/CSS/JS）
- ✅ niio API V3 整合與資料互動
- ✅ 完整的開發工作流和最佳實踐
- ✅ 自動啟動本地開發伺服器

**適用場景：**
- 企業官網（產品展示、新聞資訊、案例展示）
- 內容管理網站（部落格、文件庫、知識庫）
- 資料展示平台（資料看板、報表展示）
- 表單收集系統（線上預約、問卷調查、詢價訂單）
- 營銷落地頁（活動頁面、促銷頁面）

---

## 工作流程

### 階段 1: 需求理解與結構評估

**目標：** 理解使用者需求，評估現有 niio 應用結構

**必須執行：**
1. **讀取應用結構**
   ```javascript
   // 取得應用工作表清單
   mcp__hap_mcp____get_app_worksheets_list({
       responseFormat: 'md'
   })
   
   // 取得特定工作表結構
   mcp__hap_mcp____get_worksheet_structure({
       worksheet_id: '工作表ID',
       responseFormat: 'md',
       ai_description: '工作表: <工作表名稱>'
   })
   ```

2. **結構差距評估**
   - 識別業務物件（產品、案例、新聞等）
   - 判斷現有結構可複用性
   - 識別缺失的工作表和欄位

3. **輸出評估報告**
   - ✅ 可複用結構清單
   - ➕ 建議新增內容
   - 🚫 不執行的操作（僅分析階段）

**關鍵原則：**
- ⚠️ 此階段**僅做分析，不得執行任何寫操作**
- ✅ 必須先讀取應用現有結構
- ✅ 必須評估是否滿足需求

---

### 階段 2: 使用者確認（強制）

**目標：** 獲得使用者明確同意後再執行結構變更

**觸發條件：**
- 🔴 需要新增工作表
- 🔴 需要新增欄位到現有工作表
- 🔴 需要寫入示例資料
- 🔴 需要修改現有欄位設定

**確認方式：**
使用 `AskUserQuestion` 工具，清晰列出建議的操作：

```javascript
AskUserQuestion({
    questions: [{
        question: "根據業務需求分析，目前應用缺少「新聞資訊」相關資料表。是否允許建立新的工作表？",
        header: "新增工作表",
        multiSelect: false,
        options: [
            {
                label: "同意建立(推薦)",
                description: "建立「新聞資訊」工作表，包含標題、封面圖、釋出時間、內容等欄位，並新增 5 條示例資料"
            },
            {
                label: "僅建立表結構",
                description: "只建立工作表和欄位，不新增示例資料。前端頁面可能顯示為空"
            },
            {
                label: "暫不建立",
                description: "跳過此工作表，使用現有資料完成開發。新聞模組將無法展示"
            }
        ]
    }]
})
```

**禁止行為：**
- ❌ 未確認即新增工作表
- ❌ 未確認即新增欄位
- ❌ 未確認即寫入資料
- ❌ 假設使用者意圖

---

### 階段 3: niio 後臺設定

**目標：** 在 niio 中建立/補充資料結構和示例資料

**執行順序：**
1. **建立新工作表**（如使用者同意）
   ```javascript
   mcp__hap_mcp____create_worksheet({
       name: '新聞資訊',
       alias: 'news',
       fields: [
           { name: '標題', type: 'Text', isTitle: true, required: true },
           { name: '封面圖', type: 'Attachment', required: false },
           { name: '釋出時間', type: 'Date', required: false },
           { name: '內容', type: 'Text', required: false },
           { name: '是否釋出', type: 'Checkbox', required: false }
       ],
       ai_description: '工作表: 新聞資訊'
   })
   ```

2. **補充欄位到現有工作表**（如使用者同意）
   ```javascript
   mcp__hap_mcp____update_worksheet({
       worksheet_id: '現有工作表ID',
       addFields: [
           { name: '封面圖', type: 'Attachment' },
           { name: '詳情', type: 'Text' }
       ],
       ai_description: '工作表: <工作表名稱>'
   })
   ```

3. **新增示例資料**（如使用者同意）
   ```javascript
   // 🔴 重要：附件欄位必須填充圖片 URL
   mcp__hap_mcp____batch_create_records({
       worksheet_id: '工作表ID',
       rows: [
           {
               fields: [
                   { id: '標題欄位ID', value: '示例新聞標題' },
                   { id: '封面圖欄位ID', value: [{
                       name: 'news.jpg',
                       url: 'https://你的图片URL/示例.png'
                   }] },
                   { id: '釋出時間欄位ID', value: '2024-12-01' },
                   { id: '內容欄位ID', value: '新聞內容...' },
                   { id: '是否釋出欄位ID', value: '1' }
               ]
           }
           // ... 至少 5 條示例資料
       ],
       triggerWorkflow: false,
       ai_description: '工作表: 新聞資訊'
   })
   ```

**關鍵要求：**
- ✅ 每個新增工作表必須至少新增 **5 條示例資料**
- 🔴 **附件欄位必須填充圖片 URL**（使用文件提供的測試圖片 URL）
- ❌ 絕不允許附件欄位為空陣列 `[]` 或空字串 `''`
- ⚠️ SingleSelect/MultipleSelect 篩選必須使用 key（UUID），不能使用顯示文字

**測試圖片 URL（8個）：**
詳見 `references/niio-as-database-guide.md` 第 1.3 節

---

### 階段 4: 取得 API 憑證

**目標：** 取得 niio API 認證資訊

**方法一：透過 MCP 設定提取（推薦）**
```json
{
  "mcpServers": {
    "niio-mcp-應用名": {
      "url": "https://niiodemo.apsm.com.tw/mcp?HAP-Appkey=xxx&HAP-Sign=xxx"
    }
  }
}
```

從 URL 參數中提取：
- `HAP-Appkey`: 從 URL 參數提取
- `HAP-Sign`: 從 URL 參數提取

**方法二：手動取得**
1. 登入niio → 應用 → 設定 → API 金鑰
2. 複製 Appkey 和 Sign

**取得工作表 ID 和欄位 ID：**
- 透過 MCP: `get_worksheet_structure`
- 透過 API: `/v3/app/worksheets/{worksheetId}/structure`
- 瀏覽器審查元素: 查詢 `data-controlid` 屬性

---

### 階段 5: 前端專案建置

**目標：** 建立完整的前端專案結構

**專案結構：**
```
project-name/
├── index.html          # 主頁面
├── css/
│   └── style.css       # 樣式檔案
├── js/
│   ├── config.js       # niio 設定（Appkey、Sign、欄位對映）
│   ├── api.js          # API 封裝（請求、分頁、篩選）
│   └── main.js         # 應用邏輯（渲染、事件處理）
├── images/             # 圖片資源（可選）
└── README.md           # 專案說明
```

**核心檔案模板：**

**1. js/config.js**
```javascript
const CONFIG = {
    API_BASE_URL: 'https://niiodemo.apsm.com.tw',
    HAP_APPKEY: '你的HAP_APPKEY',
    HAP_SIGN: '你的HAP_SIGN',
    WORKSHEETS: {
        PRODUCTS: '產品表ID',
        NEWS: '新聞表ID'
    },
    PRODUCT_FIELDS: {
        NAME: '產品名稱欄位ID',
        IMAGE: '產品圖片欄位ID',
        PRICE: '參考價格欄位ID'
    }
};
```

**2. js/api.js**
- 通用請求方法（處理認證、錯誤）
- `getRows()` - 取得記錄清單（支援分頁、篩選、排序）
- `getRecord()` - 取得單條記錄詳情
- `getFieldValue()` - 通用欄位值解析函式（支援所有欄位型別）

**3. js/main.js**
- 應用初始化
- 資料載入與渲染
- 事件處理
- 錯誤處理

**4. index.html**
- 語義化 HTML 結構
- 響應式設計支援
- SEO 最佳化

**5. css/style.css**
- 現代、專業的視覺設計
- 響應式佈局
- 微互動和動畫

**詳細程式碼模板：** 參考 `references/niio-as-database-guide.md` 第 2-6 節

---

### 階段 6: API 整合

**目標：** 實現前端與 niio API V3 的資料互動

**核心要點：**

1. **CORS 跨域請求**
   ```javascript
   headers: {
       'HAP-Appkey': CONFIG.HAP_APPKEY,
       'HAP-Sign': CONFIG.HAP_SIGN,
       'Content-Type': 'application/json'
   }
   ```

2. **分頁查詢**
   ```javascript
   API.getRows(worksheetId, {
       pageIndex: 1,
       pageSize: 20,
       includeTotalCount: true,
       filter: { /* 篩選條件 */ },
       sorts: [ /* 排序 */ ]
   })
   ```

3. **欄位值解析**
   - 附件欄位：使用 `downloadUrl`
   - 選項欄位：提取 `value` 屬性
   - 關聯記錄：提取 `name` 或 `sid`
   - 檢查框：判斷 `=== '1'`

**詳細 API 使用規範：** 參考 `references/niio-api-usage-guide.md`

---

### 階段 7: 資料渲染

**目標：** 實現動態資料渲染和使用者互動

**核心要求：**
- ✅ 動態生成 DOM（使用模板字串）
- ✅ 處理空資料狀態（友好提示）
- ✅ 圖片載入失敗處理（佔點陣圖）
- ✅ 資料格式化（價格、日期等）
- ✅ 響應式佈局
- ✅ 載入狀態提示
- ✅ 錯誤處理和使用者提示

**示例：**
```javascript
async loadProducts() {
    try {
        this.showLoading();
        const data = await API.getRows(CONFIG.WORKSHEETS.PRODUCTS, {
            pageSize: 20,
            filter: {
                type: 'group',
                logic: 'AND',
                children: [{
                    type: 'condition',
                    field: CONFIG.PRODUCT_FIELDS.PUBLISHED,
                    operator: 'eq',
                    value: ['1']
                }]
            }
        });
        this.renderProducts(data.rows);
    } catch (error) {
        this.showError('載入失敗，請重新整理重試');
    } finally {
        this.hideLoading();
    }
}
```

---

### 階段 8: 啟動開發伺服器

**目標：** 自動啟動本地開發伺服器，供使用者預覽

**啟動方式（按優先順序）：**

1. **Python HTTP Server（推薦）**
   ```bash
   python -m http.server 8000
   ```

2. **npx serve**
   ```bash
   npx serve -p 8000
   ```

3. **PHP 內建伺服器**
   ```bash
   php -S localhost:8000
   ```

**執行要求：**
- ✅ 使用 `run_in_background: true` 參數
- ✅ 立即向使用者輸出訪問地址
- ✅ 埠被佔用時嘗試其他埠（8001、8080、3000）

**輸出示例：**
```
✅ 專案建置完成！
🚀 本地伺服器已啟動
📍 訪問地址: http://localhost:8000
💡 提示: 在瀏覽器中開啟上述地址即可預覽網站
```

---

## 核心原則（必須遵守）

### 1. 資料來源原則（必須動態）

✅ **允許靜態的內容：**
- 導航選單文案
- 頁尾資訊
- UI 佔位文字
- 固定的展示標題

❌ **禁止靜態的內容（必須從 niio 取得）：**
- 產品清單和詳情
- 案例展示
- 新聞資訊
- 輪播圖內容
- 價格資訊
- 任何業務相關的展示資料

### 2. 只增不刪原則（紅線）

**✅ 允許的操作：**
- 新增工作表（需確認）
- 新增欄位（需確認）
- 新增示例資料（需確認）

**❌ 嚴禁的操作：**
- 刪除任何已有工作表
- 刪除任何已有欄位
- 修改已有欄位的別名（除非使用者明確要求）
- 修改已有資料（除非使用者明確要求）

### 3. 示例資料強制要求

- ✅ 每個新增工作表必須至少新增 **5 條示例資料**
- 🔴 **附件欄位必須填充圖片 URL**（最重要！）
- ✅ 示例資料必須符合欄位型別
- ✅ 示例資料必須可直接用於前端預覽

### 4. SingleSelect/MultipleSelect 篩選規範

**🔴 重要警告：篩選必須使用 key（UUID），不能使用顯示文字！**

```javascript
// ❌ 錯誤：使用顯示文字
value: ['現代簡約']  // 篩選失敗！

// ✅ 正確：使用 key
value: ['a1b2c3d4-e5f6-7890-abcd-ef1234567890']  // 篩選成功

// 取得 key 的方法：
// 1. 呼叫 get_worksheet_structure 取得欄位的 options
// 2. 從 options 中找到匹配的 key
```

---

## 常見問題

### Q1: 如何取得欄位 ID？

**方法 1: 使用 MCP（推薦）**
```javascript
mcp__hap_mcp____get_worksheet_structure({
    worksheet_id: '工作表ID',
    responseFormat: 'md'
})
```

**方法 2: API 查詢**
```javascript
fetch('https://niiodemo.apsm.com.tw/v3/app/worksheets/{worksheetId}/structure', {
    headers: {
        'HAP-Appkey': 'xxx',
        'HAP-Sign': 'xxx'
    }
})
```

**方法 3: 瀏覽器審查元素**
- 開啟 niio 工作表
- F12 檢查元素
- 查詢 `data-controlid` 屬性

### Q2: 附件欄位如何處理？

```javascript
// 附件欄位回傳格式
const attachments = row[fieldId]; // Array
// [{downloadUrl: 'https://...', fileName: '圖片.jpg'}]

// 取得第一個附件 URL
const imageUrl = attachments[0]?.downloadUrl || '';

// 使用 niio CDN 參數最佳化
const thumbnailUrl = `${imageUrl}?imageView2/2/w/300`;
```

### Q3: 如何保護 API 金鑰安全？

**開發環境：** 可直接使用（localhost 不會洩露）

**生產環境：**
- 方案 1：使用後端代理（Node.js、PHP 等）
- 方案 2：使用 Serverless Functions（Vercel、Netlify）
- 方案 3：限制 niio API 金鑰權限（只讀權限）

### Q4: 資料量大時如何最佳化效能？

1. **分頁載入**: 設定合理的 pageSize（建議 20-50）
2. **欄位篩選**: 只取得需要的欄位
3. **前端快取**: 使用 localStorage 或記憶體快取
4. **懶載入**: 滾動到底部時載入更多
5. **防抖處理**: 搜尋框使用 debounce

---

## 參考資源

### 核心文件

- **`references/niio-as-database-guide.md`** - 完整的 niio 前後端專案建置指南
  - 專案概述和架構說明
  - 詳細步驟（niio 設定、前端建置、API 整合）
  - 核心概念和最佳實踐
  - 常見問題和解決方案

- **`references/niio-api-usage-guide.md`** - niio API V3 使用規範
  - API 端點和身分驗證與授權設定
  - 篩選器（Filter）語法詳解
  - 欄位型別處理和資料格式轉換
  - 完整的程式碼示例

### 相關技能

- **niio 檢視外掛開發指南** - 如需開發 niio 檢視外掛（與本技能不同）

---

## 工作流檢查清單

在執行本技能時，請確保完成以下所有步驟：

- [ ] **階段 1**: 讀取應用結構並評估差距
- [ ] **階段 2**: 獲得使用者確認（如需要新增結構）
- [ ] **階段 3**: 建立/補充 niio 資料結構
- [ ] **階段 3**: 新增示例資料（附件欄位必須填充圖片 URL）
- [ ] **階段 4**: 取得 API 憑證（Appkey、Sign、工作表 ID、欄位 ID）
- [ ] **階段 5**: 建立前端專案結構（HTML、CSS、JS）
- [ ] **階段 5**: 編寫設定檔案（config.js）
- [ ] **階段 5**: 編寫 API 封裝（api.js）
- [ ] **階段 5**: 編寫應用邏輯（main.js）
- [ ] **階段 6**: 實現 API 整合和資料互動
- [ ] **階段 7**: 實現資料渲染和使用者互動
- [ ] **階段 8**: 啟動本地開發伺服器並提供訪問地址

---

## 注意事項

1. **必須動態取得資料**: 業務資料必須從 niio API 取得，不能寫死在程式碼中
2. **使用者確認機制**: 任何結構變更必須徵得使用者明確同意
3. **只增不刪原則**: 絕不刪除現有工作表、欄位或資料
4. **附件欄位填充**: 示例資料的附件欄位必須填充圖片 URL
5. **篩選使用 key**: SingleSelect/MultipleSelect 篩選必須使用選項的 key（UUID）
6. **自動啟動伺服器**: 完成專案建置後必須自動啟動本地開發伺服器

---

**技能版本**: v1.0  
**最後更新**: 2026-01-11  
**適用場景**: niio 前後端分離專案建置
