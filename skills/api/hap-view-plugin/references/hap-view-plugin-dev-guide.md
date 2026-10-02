# niio 檢視外掛開發 - AI 執行手冊

> **你的任務**: 當使用者提供檢視外掛 ID 和需求描述時,你需要自動完成從專案建立到釋出上線的全流程,使用者無需手動操作任何命令。

---

## 🎯 你的工作流程

### 當使用者說:"幫我建立一個 XXX 檢視外掛,ID 是 xxx-yyy" 時:

```
第1步: 檢查並安裝 mdye-cli
第2步: 根據需求選擇模板並建立專案
第3步: 安裝依賴
第4步: 根據需求編寫程式碼（在模板基礎上修改或完全重寫）
第5步: 啟動開發伺服器(後臺執行,靜默執行)
第6步: 等待使用者反饋並修改程式碼
第7步: 使用者確認後建置併發布
```

**⚠️ 重要提醒：**
- niio 提供多種官方模板（JavaScript、React、React-Tailwind、Vue）
- 模板已包含基礎結構，你**不需要從零編寫所有程式碼**
- 根據使用者需求選擇合適的模板，然後在模板基礎上修改

---

## 第1步: 環境檢查

### 你需要做:

```bash
# 檢查 mdye-cli 是否已安裝
mdye --version
```

**如果輸出版本號** → 跳過,進入第2步

**如果提示"command not found"** → 執行安裝:

```bash
# macOS/Linux
sudo npm install -g mdye-cli

# Windows
npm install -g mdye-cli
```

**安裝後驗證:**

```bash
mdye --version
# 應該輸出類似: beta-0.0.37
```

---

## 第2步: 建立專案

### niio 提供的官方模板

niio 提供多種外掛模板，透過 `--template` 參數選擇：

| 模板名稱 | 適用場景 | 技術棧 |
|---------|---------|-------|
| `JavaScript` | 基礎外掛、簡單展示 | 原生 JS + HTML |
| `React` | 互動複雜的外掛 | React + Hooks |
| `React-Tailwind` | 需要快速樣式開發 | React + Tailwind CSS |
| `Vue` | Vue 技術棧專案 | Vue 3 |

### 你需要做:

**根據使用者需求選擇合適的模板：**

```bash
# 使用者會給你一個 ID，格式類似:
# 你的worksheetID-你的檢視ID

# 1. JavaScript 基礎模板（簡單展示）
echo "view-plugin" | mdye init view --id <使用者提供的ID> --template JavaScript

# 2. React 模板（推薦，互動複雜場景）
echo "view-plugin" | mdye init view --id <使用者提供的ID> --template React

# 3. React + Tailwind CSS 模板（需要快速樣式開發）
echo "view-plugin" | mdye init view --id <使用者提供的ID> --template React-Tailwind

# 4. Vue 模板
echo "view-plugin" | mdye init view --id <使用者提供的ID> --template Vue
```

**模板選擇建議：**

- 📊 **資料看板、BI 駕駛艙** → `React` 或 `React-Tailwind`
- 📅 **日曆、甘特圖** → `React`
- 🗺️ **地圖檢視** → `React`
- 📝 **簡單清單、卡片展示** → `JavaScript` 或 `React-Tailwind`

**執行後會:**
- 建立名為 `view-plugin` 的專案目錄
- 自動生成對應模板的程式碼

### 進入專案目錄:

```bash
cd view-plugin
```

---

## 第3步: 安裝依賴

### 你需要做:

```bash
# 基礎依賴
npm install

# 根據使用者需求安裝額外依賴:
# 如果是 BI 駕駛艙 → 安裝 recharts
npm install recharts

# 如果需要樣式庫 → 安裝 styled-components
npm install styled-components

# 如果需要日期處理 → 安裝 dayjs
npm install dayjs
```

**常見場景對應的依賴:**

| 使用者需求 | 需要安裝的依賴 |
|---------|---------------|
| 訂單看板/任務看板 | styled-components |
| BI駕駛艙/資料分析 | recharts, styled-components |
| 日曆檢視 | dayjs, styled-components |
| 地圖檢視 | (無額外依賴,使用外部地圖 SDK) |

---

## 第4步: 編寫程式碼

### 你需要做:

使用 **Write 工具** 完全覆蓋模板生成的程式碼檔案，生成符合使用者需求的程式碼。

**程式碼檔案位置：**
- React/React-Tailwind 模板：`src/App.js` 或 `src/App.jsx`
- Vue 模板：`src/App.vue`
- JavaScript 模板：`src/index.js`

### 程式碼編寫原則:

#### 1. 模板已包含基礎結構（可直接使用或修改）

niio 官方模板已經包含了必要的基礎結構，你**不需要從零編寫**。你可以：
- ✅ 在模板基礎上修改和擴充套件
- ✅ 完全重寫以滿足特定需求
- ✅ 保留模板的資料取得邏輯，只修改展示部分

**React 模板的典型基礎結構：**

```javascript
import React, { useState, useEffect } from 'react';
import { api, config, utils } from 'mdye';

export default function App() {
  const { appId, worksheetId, viewId, controls } = config;
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      setLoading(true);
      const result = await api.getFilterRows({
        worksheetId,
        viewId,
        pageSize: 100
      });
      setRecords(result.data || []);
    } catch (err) {
      console.error('載入失敗:', err);
    } finally {
      setLoading(false);
    }
  }

  const handleRecordClick = async (recordId) => {
    const result = await utils.openRecordInfo({
      appId,
      worksheetId,
      viewId,
      recordId
    });

    if (result && result.action === 'update') {
      loadData();
    }
  };

  if (loading) {
    return <div>載入中...</div>;
  }

  return (
    <Container>
      {/* 根據使用者需求渲染 UI */}
    </Container>
  );
}
```

#### 2. 正確處理欄位型別:

**單選欄位 (type 9) 解析:**

```javascript
function parseSingleSelect(value, control) {
  try {
    if (!value) return { key: "", text: "" };
    const keys = typeof value === 'string' ? JSON.parse(value) : value;
    const selectedKey = keys[0] || "";
    const option = control?.options?.find(opt => opt.key === selectedKey);
    return { key: selectedKey, text: option?.value || "" };
  } catch (err) {
    return { key: "", text: "" };
  }
}

// 使用:
const statusControl = controls.find(c => c.type === 9 && c.controlName?.includes('狀態'));
const status = parseSingleSelect(record[statusControl.controlId], statusControl);
// status.text 就是顯示文字,如"已完成"
```

**多條關聯欄位 (type 29) 解析:**

```javascript
// 多條關聯回傳的是數字(關聯記錄數量),需要呼叫 API 取得詳情
async function loadRelationData(worksheetId, controlId, rowId, fieldValue) {
  if (typeof fieldValue === 'number') {
    const result = await api.getRowRelationRows({
      worksheetId,
      controlId,
      rowId,
      pageSize: 100,
      pageIndex: 1
    });
    return result.data || [];
  } else {
    // 單條關聯,直接解析 JSON
    try {
      return typeof fieldValue === 'string' ? JSON.parse(fieldValue) : fieldValue;
    } catch {
      return [];
    }
  }
}
```

#### 3. 根據使用者需求選擇模板:

**場景A: 按狀態分組的看板檢視**

使用者說: "建立訂單看板" / "任務看板" / "按狀態展示"

你需要生成:
- 按狀態列位分組
- 卡片式展示每個訂單/任務
- 點選卡片開啟詳情
- 顯示關鍵欄位(標題、金額、負責人等)

**核心程式碼:**
```javascript
// 按狀態分組
const grouped = records.reduce((acc, record) => {
  const status = parseSingleSelect(record[statusFieldId], statusControl).text;
  if (!acc[status]) acc[status] = [];
  acc[status].push(record);
  return acc;
}, {});

// 渲染分組
return (
  <Container>
    {Object.entries(grouped).map(([status, items]) => (
      <StatusSection key={status}>
        <h2>{status} ({items.length})</h2>
        <CardsGrid>
          {items.map(item => (
            <Card key={item.rowid} onClick={() => handleRecordClick(item.rowid)}>
              {/* 渲染卡片內容 */}
            </Card>
          ))}
        </CardsGrid>
      </StatusSection>
    ))}
  </Container>
);
```

**場景B: BI 駕駛艙**

使用者說: "建立 CRM 駕駛艙" / "資料分析面板" / "業務概覽"

你需要生成:
- 頂部核心指標卡片(總數、完成率、金額等)
- 中部圖表(柱狀圖、餅圖、趨勢圖)
- 使用 recharts 庫

**核心程式碼:**
```javascript
// 計算指標
const metrics = {
  total: records.length,
  completed: records.filter(r => getStatus(r) === '已完成').length,
  revenue: records.reduce((sum, r) => sum + (parseFloat(r.amount) || 0), 0)
};

// 準備圖表資料
const chartData = Object.entries(grouped).map(([key, items]) => ({
  name: key,
  value: items.length,
  amount: items.reduce((sum, item) => sum + (parseFloat(item.amount) || 0), 0)
}));

// 渲染
return (
  <Dashboard>
    {/* 指標卡片 */}
    <MetricsGrid>
      <MetricCard>
        <h3>總數</h3>
        <div className="value">{metrics.total}</div>
      </MetricCard>
      {/* 更多指標... */}
    </MetricsGrid>

    {/* 圖表 */}
    <ChartCard>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="value" fill="#1890ff" />
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  </Dashboard>
);
```

**場景C: 清單檢視**

使用者說: "建立客戶清單" / "顯示所有記錄"

你需要生成:
- 表格或卡片清單
- 顯示關鍵欄位
- 支援點選檢視詳情

---

## 第5步: 啟動開發伺服器

### 你需要做:

```bash
mdye start
# 重要: 使用 run_in_background: true 參數
```

**關鍵點:**
- ✅ 伺服器會在後臺持續執行
- ✅ **靜默執行,不要告訴使用者任何除錯地址或技術細節**
- ✅ 不要主動關閉伺服器
- ✅ 只有使用者明確說"停止伺服器"或"關閉開發服務"時才執行 kill

**伺服器啟動後:**
- 監聽 http://localhost:3000/bundle.js (或 3001 等埠)
- 自動熱更新程式碼變化
- **使用者在niio後臺已經設定了這個地址,無需你告知**

**❌ 嚴禁輸出的內容:**
- ❌ 除錯地址 (如 http://localhost:3000/bundle.js)
- ❌ "請複製到niio..."之類的指引
- ❌ 專案結構說明
- ❌ 命令執行日誌
- ❌ "啟動完成"、"編譯成功"等技術狀態
- ❌ "接下來您可以..."之類的引導
- ❌ 任何需要使用者手動操作的說明

**✅ 正確的做法:**
啟動伺服器後,**保持完全靜默**,直接等待使用者反饋,或者簡單回覆:
```
已完成,請在niio中檢視效果。
```

---

## 第6步: 等待使用者反饋並修改程式碼

### 使用者可能會說:

- "把卡片背景改成藍色"
- "字型太小了,改大一點"
- "能不能加個搜尋功能"
- "這個欄位顯示不對"

### 你需要做:

1. 使用 **Edit 工具** 修改 `src/App.js` 檔案
2. 熱更新會自動生效
3. **簡單回覆**: "已修改"

**示例:**

使用者說: "把金額字型改成 24px"

你執行:
```bash
# 使用 Edit 工具修改
old_string: "font-size: 20px;"
new_string: "font-size: 24px;"
```

然後回覆: "已修改"

**❌ 不要說:**
- "已修改金額字型大小,請重新整理niio頁面檢視效果"
- "修改完成,熱更新已生效,請檢視"
- 任何技術細節或指引

---

## 第7步: 建置併發布

### 使用者會說:

- "可以了,幫我釋出吧"
- "沒問題,上線吧"
- "釋出到生產環境"

### 你需要做:

```bash
# 第1步: 建置
mdye build

# 第2步: 釋出
mdye push -m "檢視外掛釋出說明"
```

**釋出說明格式:**

```bash
mdye push -m "訂單看板檢視首次釋出

功能特性:
- 按訂單狀態分組展示(待付款/已付款/已發貨/已完成)
- 顯示訂單編號、客戶名稱、訂單金額
- 點選卡片開啟niio原生詳情彈窗
- 支援編輯訂單並自動重新整理清單
- 響應式佈局適配移動端

技術實現:
- 使用 utils.openRecordInfo 原生互動
- 正確處理單選欄位(type 9)
- 按狀態分組並統計數量
- 新增載入狀態和錯誤處理"
```

**釋出成功後,簡單回覆:**

```
已釋出
```

**❌ 不要說:**
- "🎉 檢視外掛已釋出成功!"
- "已釋出到niio平台,現在可以在所有應用中使用這個檢視了"
- "檢視地址: xxx"
- "如需修改,隨時告訴我"
- 任何多餘的說明和引導

---

## 常見場景速查

### 場景1: 訂單/任務看板

**使用者需求:** "建立一個訂單看板,按狀態分組"

**你的執行流程:**
1. 安裝依賴: `npm install styled-components`
2. 生成程式碼: 按狀態分組的卡片佈局
3. 關鍵點:
   - 解析單選欄位取得狀態文字
   - 使用 `utils.openRecordInfo` 開啟詳情
   - 響應式網格佈局

### 場景2: CRM/銷售駕駛艙

**使用者需求:** "建立 CRM 管理駕駛艙"

**你的執行流程:**
1. 安裝依賴: `npm install recharts styled-components`
2. 生成程式碼: 指標卡片 + 圖表
3. 關鍵點:
   - 計算核心指標(總數、轉化率、金額)
   - 使用 recharts 渲染柱狀圖/餅圖
   - 按業務維度分組統計

### 場景3: 客戶清單

**使用者需求:** "建立客戶清單檢視"

**你的執行流程:**
1. 安裝依賴: `npm install styled-components`
2. 生成程式碼: 卡片或表格清單
3. 關鍵點:
   - 顯示關鍵欄位(名稱、電話、負責人)
   - 點選開啟詳情
   - 簡潔佈局

---

## 欄位型別處理速查

### 必須記住:

| 欄位型別 | type | 回傳值格式 | 處理方法 |
|---------|------|-----------|---------|
| 文字 | 2 | 字串 | 直接使用 |
| 數值 | 6 | 字串/數字 | parseFloat() |
| **單選** | **9** ⚠️ | JSON字串陣列 | 解析 JSON + 從 options 匹配文字 |
| 多選 | 10 | JSON字串陣列 | 同單選,但回傳陣列 |
| 日期 | 15 | 時間戳字串 | new Date() 或 dayjs() |
| 成員 | 26 | JSON字串陣列 | 解析 JSON 取得 accountId/fullname |
| **關聯記錄** | **29** ⚠️ | 數字(多條) / JSON(單條) | 數字需呼叫 getRowRelationRows API |

### 最容易出錯的兩個:

**1. 單選欄位不是 type 11,是 type 9!**

```javascript
// ❌ 錯誤
const field = controls.find(c => c.type === 11);

// ✅ 正確
const field = controls.find(c => c.type === 9);
```

**2. 多條關聯不能直接用,要調 API!**

```javascript
// ❌ 錯誤: 顯示 "2" 而不是實際關聯記錄
<div>{record.relationField}</div>

// ✅ 正確: 判斷是否為數字,然後調 API
if (typeof record.relationField === 'number') {
  const relations = await api.getRowRelationRows({
    worksheetId,
    controlId: relationFieldId,
    rowId: record.rowid,
    pageSize: 100
  });
  // 使用 relations.data
}
```

---

## 錯誤處理速查

### 如果遇到錯誤:

| 錯誤 | 原因 | 你的操作 |
|------|------|---------|
| mdye: command not found | 未安裝 | 執行 `sudo npm install -g mdye-cli` |
| npm install 失敗 | 網路或快取問題 | 執行 `npm cache clean --force` 然後重試 |
| mdye start 失敗 | 埠占用 | 檢查 3000 埠,或使用其他埠 |
| 單選欄位顯示 UUID | 未解析選項 | 使用 parseSingleSelect 函式 |
| 關聯欄位顯示數字 | 未呼叫 API | 檢查是否為 number,呼叫 getRowRelationRows |
| mdye build 失敗 | 程式碼語法錯誤 | 檢查 console 錯誤,修復程式碼 |

---

## 檢查清單

**在告訴使用者"已完成"之前,確認:**

- [ ] mdye-cli 已安裝
- [ ] 專案已建立並進入目錄
- [ ] npm install 執行成功
- [ ] 程式碼已生成(src/App.js)
- [ ] mdye start 已啟動(後臺執行)
- [ ] 已告訴使用者除錯地址
- [ ] 使用者測試並確認無誤
- [ ] mdye build 執行成功
- [ ] mdye push 執行成功
- [ ] 已告訴使用者檢視地址

---

## 重要提醒

### 你必須自動完成的操作:

- ✅ 檢查並安裝 mdye-cli
- ✅ 執行 mdye init view
- ✅ 執行 npm install
- ✅ 編寫程式碼(使用 Write/Edit 工具)
- ✅ 執行 mdye start(後臺執行)
- ✅ 執行 mdye build
- ✅ 執行 mdye push

### 你不應該做的:

- ❌ 告訴使用者"您需要執行..."
- ❌ 說"接下來請執行..."
- ❌ 主動關閉開發伺服器
- ❌ 等使用者要求才建置釋出
- ❌ 展示技術細節和命令輸出
- ❌ **告訴使用者除錯地址 (如 http://localhost:3000/bundle.js)**
- ❌ **告訴使用者"複製到niio..."之類的操作指引**
- ❌ **輸出"啟動完成"、"編譯成功"等技術狀態**
- ❌ **說"請重新整理niio頁面檢視效果"**

### 你只需告訴使用者的:

**完成程式碼編寫後:**
```
已完成,請在niio中檢視效果。
```

**使用者要求修改後:**
```
已修改
```

**使用者要求釋出後:**
```
已釋出
```

**就這麼簡單,不要多說一個字!**

---

**記住: 使用者只想要結果,不關心過程。你的目標是讓整個流程對使用者來說完全透明且自動化。使用者已經知道怎麼在niio後臺檢視和設定,不需要你教他!** 🚀

---

## API 使用指南

### 1. 環境變數及設定取得

#### 1.1 取得 env 環境變數

```javascript
// 使用輔助函式安全取得env中的設定項
function getEnvValue(env, key, defaultValue = null) {
  if (!env || !key) return defaultValue;

  const value = env[key];

  // 處理陣列型別(欄位選擇器)
  if (Array.isArray(value)) {
    return value.length > 0 ? value[0] : defaultValue;
  }

  // 處理普通值
  return value !== undefined ? value : defaultValue;
}

// 使用示例
const titleFieldId = getEnvValue(env, 'title');
const maxRecords = getEnvValue(env, 'maxRecords', '50');
```

#### 1.2 取得 config 設定

```javascript
import { config } from "mdye";

// 取得應用、工作表、檢視的ID
const { appId, worksheetId, viewId, controls } = config;

// 取得欄位控制元件資訊
const fieldControl = _.find(controls, { controlId: fieldId });
```

### 2. 資料取得 API

#### 2.1 取得工作表資料 (getFilterRows)

```javascript
import { api } from "mdye";

async function loadRecords() {
  const result = await api.getFilterRows({
    worksheetId,     // 必填-工作表ID
    viewId,          // 必填-檢視ID
    pageIndex: 1,    // 可選-頁碼
    pageSize: 50,    // 可選-每頁記錄數
    sortId: "fieldId", // 可選-排序欄位
    isAsc: true,     // 可選-升序排序
    // 取得關聯欄位資料
    requestParams: {
      plugin_detail_control: relationFieldId
    }
  });

  return result.data; // 記錄陣列
}
```

#### 2.2 取得記錄詳情 (getRowDetail)

```javascript
async function getRecordDetail(rowId) {
  const result = await api.getRowDetail({
    appId,
    worksheetId,
    viewId,
    rowId
  });

  return result.data;
}
```

#### 2.3 取得關聯記錄 (getRowRelationRows)

```javascript
async function loadRelationRows({ controlId, rowId }) {
  const result = await api.getRowRelationRows({
    worksheetId,
    controlId,       // 關聯欄位ID
    rowId,           // 主記錄ID
    pageIndex: 1,
    pageSize: 10
  });

  return result.data;
}
```

### 3. 資料操作 API

#### 3.1 新增記錄 (addWorksheetRow)

```javascript
async function addRecord(fieldsData) {
  const response = await api.addWorksheetRow({
    appId,
    worksheetId,
    receiveControls: [
      {
        controlId: "fieldId1",
        type: 2,
        value: "測試文字"
      }
    ]
  });
  return response;
}
```

#### 3.2 更新記錄 (updateWorksheetRow)

```javascript
async function updateRecord(rowId, fieldId, newValue) {
  const response = await api.updateWorksheetRow({
    appId,
    worksheetId,
    rowId,
    newOldControl: [
      {
        controlId: fieldId,
        type: 2,
        value: newValue
      }
    ]
  });
  return response;
}
```

#### 3.3 刪除記錄 (deleteWorksheetRow)

```javascript
async function deleteRecord(rowId) {
  const response = await api.deleteWorksheetRow({
    appId,
    worksheetId,
    rowIds: [rowId]
  });
  return response;
}
```

### 4. 工具函式 (utils)

#### 4.1 開啟記錄詳情（推薦使用！）

**使用 `utils.openRecordInfo` 開啟niio原生行記錄元件是最佳實踐:**

優勢:
- ✅ 原生體驗,與niio介面一致
- ✅ 功能完整:支援編輯、刪除、討論、日誌、附件等所有功能
- ✅ 自動處理權限驗證
- ✅ 無需自己開發彈窗 UI
- ✅ 回傳操作結果,方便進行資料同步

**基礎用法:**

```javascript
import { utils } from "mdye";

// 開啟記錄詳情
const handleRecordClick = async (recordId) => {
  try {
    const result = await utils.openRecordInfo({
      appId,
      worksheetId,
      viewId,
      recordId
    });

    // 處理回傳結果
    if (result) {
      console.log('操作結果:', result);

      // 根據操作型別處理
      switch (result.action) {
        case 'update':
          // 記錄被更新,重新整理資料
          console.log('記錄已更新:', result.value);
          loadRecords(); // 重新載入資料
          break;
        case 'delete':
          // 記錄被刪除,重新整理清單
          console.log('記錄已刪除');
          loadRecords(); // 重新載入資料
          break;
        case 'close':
          // 使用者關閉彈窗(無修改)
          console.log('使用者關閉了彈窗');
          break;
      }
    }
  } catch (error) {
    console.error('開啟記錄詳情失敗:', error);
  }
};
```

#### 4.2 開啟新建記錄視窗

```javascript
utils.openNewRecord({
  appId,
  worksheetId
}).then(newRecord => {
  if (newRecord) {
    addLocalRecord(newRecord);
  }
});
```

#### 4.3 選擇使用者

```javascript
const users = await utils.selectUsers({
  projectId: "orgId1",
  unique: false  // 是否單選
});
```

#### 4.4 選擇記錄

```javascript
const records = await utils.selectRecord({
  projectId: "orgId1",
  relateSheetId: "worksheetId1",
  multiple: true
});
```

### 5. 事件監聽

#### 5.1 篩選條件變更事件

```javascript
import { md_emitter } from "mdye";

useEffect(() => {
  const handleFiltersUpdate = (newFilters) => {
    console.log('篩選條件已更新:', newFilters);
    // 重新取得資料
  };

  md_emitter.addListener('filters-update', handleFiltersUpdate);

  return () => {
    md_emitter.removeListener('filters-update', handleFiltersUpdate);
  };
}, []);
```

#### 5.2 新增記錄事件

```javascript
useEffect(() => {
  const handleNewRecord = (newRecord) => {
    console.log('新增記錄:', newRecord);
    setRecords(prev => [...prev, newRecord]);
  };

  md_emitter.addListener('new-record', handleNewRecord);

  return () => {
    md_emitter.removeListener('new-record', handleNewRecord);
  };
}, []);
```

---

## 欄位型別處理

### ⚠️ 重要提示:欄位型別編號

**niio欄位型別編號與文件中的列舉值不完全一致,開發時務必注意:**

根據niio API V3 版本的實際欄位型別定義:
- **Type 9** = 單選 (SingleSelect) ⚠️ 注意不是 type 11
- **Type 10** = 多選 (MultipleSelect)
- **Type 11** = 下拉 (Dropdown)

### 完整欄位型別對照表

| 型別編號 | 列舉名稱 | 欄位型別 | API 建立 | API 回傳 |
|---------|---------|---------|---------|---------|
| 2 | Text | 文字框 | ✅ | ✅ |
| 3 | PhoneNumber | 手機 | ❌ | ✅ |
| 4 | LandlinePhone | 座機 | ❌ | ✅ |
| 5 | Email | 郵箱 | ❌ | ✅ |
| 6 | Number | 數值 | ✅ | ✅ |
| 7 | Certificate | 證件 | ❌ | ✅ |
| 8 | Currency | 金額 | ❌ | ✅ |
| **9** | **SingleSelect** | **單選** | ✅ | ✅ |
| 10 | MultipleSelect | 多選 | ✅ | ✅ |
| 11 | Dropdown | 下拉 | ❌ | ✅ |
| 14 | Attachment | 附件 | ✅ | ✅ |
| 15 | Date | 日期 | ✅ | ✅ |
| 16 | DateTime | 時間 | ✅ | ✅ |
| 19/23/24 | Region | 地區 | ❌ | ✅ |
| 26 | Collaborator | 成員 | ✅ | ✅ |
| 27 | Department | 部門 | ❌ | ✅ |
| 28 | Rating | 等級 | ❌ | ✅ |
| 29 | Relation | 連線他表 | ✅ | ✅ |
| 30 | Lookup | 他表欄位 | ❌ | ✅ |
| 31 | Formula | 公式 | ❌ | ✅ |
| 34 | SubTable | 子表 | ❌ | ✅ |
| 36 | Checkbox | 檢查框 | ❌ | ✅ |
| 40 | Location | 定位 | ❌ | ✅ |
| 41 | RichText | 富文字 | ❌ | ✅ |
| 42 | Signature | 簽名 | ❌ | ✅ |
| 46 | Time | 時間 | ✅ | ✅ |

### 欄位解析函式

#### 單選欄位

```javascript
function parseSingleSelect(value, control) {
  try {
    if (!value) return { key: "", text: "" };

    const keys = typeof value === 'string'
      ? JSON.parse(value)
      : (Array.isArray(value) ? value : []);

    const selectedKey = keys[0] || "";

    let selectedText = "";
    if (control && control.options) {
      const option = control.options.find(opt => opt.key === selectedKey);
      selectedText = option ? option.value : "";
    }

    return { key: selectedKey, text: selectedText };
  } catch (err) {
    console.error("解析單選欄位失敗:", err);
    return { key: "", text: "" };
  }
}
```

#### 多選欄位

```javascript
function parseMultiSelect(value, control) {
  try {
    if (!value) return [];

    const keys = typeof value === 'string'
      ? JSON.parse(value)
      : (Array.isArray(value) ? value : []);

    const result = [];
    if (control && control.options) {
      keys.forEach(key => {
        const option = control.options.find(opt => opt.key === key);
        if (option) {
          result.push({ key: key, text: option.value });
        }
      });
    }

    return result;
  } catch (err) {
    console.error("解析多選欄位失敗:", err);
    return [];
  }
}
```

#### 關聯記錄欄位（⚠️ 重要！）

**關聯欄位 (type 29) 的特殊處理規則:**

關聯欄位根據 `enumDefault` 或 `subType` 屬性分為兩種型別:

1. **單條關聯** (enumDefault=1 或 subType=1)
   - 回傳格式: JSON 陣列字串
   - 處理方式: 直接解析 JSON 字串即可

2. **多條關聯** (enumDefault=2 或 subType=2)
   - 回傳格式: 數字(表示關聯記錄的數量)
   - 處理方式: **必須呼叫 `getRowRelationRows` API** 才能取得實際資料

```javascript
// 判斷是否為多條關聯
function isMultipleRelation(value) {
  return typeof value === 'number' || (!isNaN(value) && value !== '');
}

// 解析單條關聯資料
function parseRelationData(value) {
  try {
    if (!value) return [];

    const relations = typeof value === 'string' ? JSON.parse(value) : value;
    if (!Array.isArray(relations)) return [];

    return relations.map(item => ({
      sid: item.sid || '',
      name: item.name || '',
      ...item
    }));
  } catch (err) {
    console.error("解析關聯記錄欄位失敗:", err);
    return [];
  }
}

// 完整處理示例
async function handleRelationField(worksheetId, controlId, rowId, fieldValue) {
  let relationData = [];

  if (isMultipleRelation(fieldValue)) {
    // 多條關聯:呼叫 API 取得詳情
    const result = await api.getRowRelationRows({
      worksheetId,
      controlId,
      rowId,
      pageSize: 100,
      pageIndex: 1
    });

    if (result && result.data) {
      relationData = result.data;
    }
  } else {
    // 單條關聯:直接解析
    relationData = parseRelationData(fieldValue);
  }

  return relationData;
}
```

#### 附件欄位

```javascript
function parseAttachments(value) {
  try {
    if (!value) return [];
    return typeof value === 'string' ? JSON.parse(value) : value;
  } catch (err) {
    return [];
  }
}
```

#### 成員欄位

```javascript
function parseMembers(value) {
  try {
    if (!value) return [];
    return typeof value === 'string' ? JSON.parse(value) : value;
  } catch (err) {
    return [];
  }
}
```

### 自動取得欄位值的工具函式

```javascript
function getFieldValue(fieldId, record, controls) {
  if (!fieldId || !record) return null;

  const rawValue = record[fieldId];
  if (rawValue === undefined) return null;

  const control = controls.find(ctrl => ctrl.controlId === fieldId);
  if (!control) return rawValue;

  const fieldType = getFieldTypeByControlType(control.type);

  switch (fieldType) {
    case 'text':
    case 'email':
    case 'phone':
      return rawValue;

    case 'number':
      return parseFloat(rawValue) || 0;

    case 'select':
      return parseSingleSelect(rawValue, control);

    case 'multiselect':
      return parseMultiSelect(rawValue, control);

    case 'user':
      return parseMembers(rawValue);

    case 'attachment':
      return parseAttachments(rawValue);

    case 'boolean':
      return rawValue === "1" || rawValue === 1 || rawValue === true;

    case 'relation':
      return parseRelationData(rawValue);

    default:
      return rawValue;
  }
}

function getFieldTypeByControlType(controlType) {
  const typeMap = {
    2: 'text',           // 文字框
    3: 'phone',          // 手機
    4: 'phone',          // 座機
    5: 'email',          // 郵箱
    6: 'number',         // 數值
    7: 'certificate',    // 證件
    8: 'number',         // 金額
    9: 'select',         // 單選 ⚠️ 重要:type 9 是單選
    10: 'multiselect',   // 多選
    11: 'select',        // 下拉
    14: 'attachment',    // 附件
    15: 'date',          // 日期
    16: 'datetime',      // 時間
    19: 'region',        // 地區
    23: 'region',        // 地區
    24: 'region',        // 地區
    26: 'user',          // 成員
    27: 'department',    // 部門
    28: 'rating',        // 等級
    29: 'relation',      // 連線他表
    36: 'boolean',       // 檢查框
    40: 'location',      // 定位
    41: 'richtext',      // 富文字
    42: 'signature',     // 簽名
    46: 'time',          // 時間
    48: 'role',          // 組織角色
  };
  return typeMap[controlType] || 'unknown';
}
```

---

## V3 介面整合

### 資料操作方式對比

niio niio 檢視外掛支援兩種資料操作方式:

#### 1. 使用外掛內部函式和元件 (mdye API)

**適用場景:** 檢視外掛內的標準資料操作

**特點:**
- ✅ 已封裝好身分驗證與授權,開箱即用
- ✅ 自動處理權限和上下文
- ✅ 提供完整的 TypeScript 型別定義
- ✅ 與niio原生 UI 元件整合
- ⚠️ 僅限當前工作表和檢視的資料操作
- ⚠️ 部分高階功能未封裝

**推薦使用的內部函式:**
```javascript
import { api, utils, config, md_emitter } from 'mdye';

// 取得當前檢視資料
api.getFilterRows({ worksheetId, viewId });

// 開啟原生記錄詳情彈窗
utils.openRecordInfo({ appId, worksheetId, viewId, recordId });

// 取得工作表結構資訊
config.controls; // 欄位清單
```

#### 2. 使用 niio V3 公開介面 (REST API)

**適用場景:**
- ✅ 需要呼叫 mdye 未封裝的介面
- ✅ 跨工作表、跨應用的資料操作
- ✅ 建置複雜的業務邏輯頁面
- ✅ 使用高階功能（選項集、角色、工作流等）
- ✅ 批次資料匯入匯出
- ✅ 自訂資料聚合統計

**特點:**
- ✅ 完整的 RESTful API
- ✅ 支援所有niio功能
- ✅ 可在任何環境使用(外掛/獨立頁面)
- ✅ 靈活的資料篩選和排序
- ⚠️ 需要手動設定身分驗證與授權(Appkey & Sign)
- ⚠️ 需要處理跨域問題（外掛內無此問題）

### 在檢視外掛中使用 V3 介面建置複雜頁面

#### 方案1: 使用 mdye 封裝的 api（推薦用於當前表操作）

```javascript
import { api, config } from 'mdye';

const { appId, worksheetId, viewId } = config;

// 已包含身分驗證與授權,直接呼叫
const result = await api.getFilterRows({
  worksheetId,
  viewId,
  pageSize: 50
});
```

**侷限性:**
- 僅限當前工作表和檢視
- 無法訪問其他工作表資料
- 部分高階功能（選項集、角色、聚合查詢）未封裝

#### 方案2: 直接呼叫 V3 介面（推薦用於複雜業務場景）

**✅ 適用場景示例:**
1. **多表關聯展示** - 在一個檢視中展示多個工作表的資料
2. **跨應用資料整合** - 從多個應用匯總資料
3. **高階資料統計** - 使用透視表API進行復雜聚合
4. **選項集管理** - 動態載入和使用應用選項集
5. **角色權限控制** - 根據使用者角色顯示不同內容
6. **批次資料操作** - 批次建立、更新記錄

**設定步驟:**

**第1步：設定身分驗證與授權資訊**

```javascript
// 在專案根目錄建立 config/api.config.js
const API_CONFIG = {
  baseUrl: 'https://api.mingdao.com',
  appkey: 'YOUR_APPKEY',  // 從niio後臺取得
  sign: 'YOUR_SIGN'       // 從niio後臺取得
};

export default API_CONFIG;
```

**第2步：封裝通用請求函式**

```javascript
// utils/v3Api.js
import API_CONFIG from '../config/api.config';

class V3Api {
  constructor(config) {
    this.baseUrl = config.baseUrl;
    this.headers = {
      'Content-Type': 'application/json',
      'HAP-Appkey': config.appkey,
      'HAP-Sign': config.sign
    };
  }

  async request(endpoint, method = 'GET', body = null) {
    const options = {
      method,
      headers: this.headers
    };

    if (body) {
      options.body = JSON.stringify(body);
    }

    try {
      const response = await fetch(
        `${this.baseUrl}${endpoint}`,
        options
      );

      const data = await response.json();

      if (data.success) {
        return data;
      } else {
        throw new Error(data.error_msg || '請求失敗');
      }
    } catch (error) {
      console.error('API請求錯誤:', error);
      throw error;
    }
  }

  // GET 請求
  async get(endpoint) {
    return await this.request(endpoint, 'GET');
  }

  // POST 請求
  async post(endpoint, body) {
    return await this.request(endpoint, 'POST', body);
  }

  // PUT 請求
  async put(endpoint, body) {
    return await this.request(endpoint, 'PUT', body);
  }

  // DELETE 請求
  async delete(endpoint, body) {
    return await this.request(endpoint, 'DELETE', body);
  }
}

export default new V3Api(API_CONFIG);
```

**第3步：封裝業務介面**

```javascript
// api/worksheet.js
import v3Api from '../utils/v3Api';

// 取得工作表記錄清單
export async function getRecordList(worksheetId, options = {}) {
  const endpoint = `/v3/app/worksheets/${worksheetId}/rows/list`;

  const body = {
    pageSize: options.pageSize || 100,
    pageIndex: options.pageIndex || 1,
    filter: options.filter || null,
    sorts: options.sorts || [],
    search: options.search || '',
    useFieldIdAsKey: true,
    includeTotalCount: options.includeTotalCount || false
  };

  const result = await v3Api.post(endpoint, body);
  return result.data || { rows: [], total: 0 };
}

// 取得工作表結構
export async function getWorksheetStructure(worksheetId) {
  const endpoint = `/v3/app/worksheets/${worksheetId}/structure`;
  const result = await v3Api.get(endpoint);
  return result.data;
}

// 取得透視表統計資料
export async function getPivotData(worksheetId, config) {
  const endpoint = `/v3/app/worksheets/${worksheetId}/rows/pivot`;

  const body = {
    values: config.values,      // 統計欄位設定
    rows: config.rows || [],    // 行維度欄位
    columns: config.columns || [], // 列維度欄位
    filter: config.filter || null,
    pageSize: config.pageSize || 1000,
    pageIndex: config.pageIndex || 1
  };

  const result = await v3Api.post(endpoint, body);
  return result.data;
}

// 取得選項集清單
export async function getOptionSets() {
  const endpoint = '/v3/app/optionsets';
  const result = await v3Api.get(endpoint);
  return result.data;
}

// 取得角色清單
export async function getRoles() {
  const endpoint = '/v3/app/roles';
  const result = await v3Api.get(endpoint);
  return result.data;
}
```

### 實戰案例：跨表資料整合檢視

#### 需求場景
在一個檢視外掛中展示：
- **客戶工作表**的客戶資訊
- **訂單工作表**的訂單統計
- **產品工作表**的熱銷產品
- 使用**選項集**統一狀態顯示

#### 完整實現程式碼

```javascript
// App.jsx
import React, { useState, useEffect } from 'react';
import { getRecordList, getPivotData, getOptionSets } from './api/worksheet';
import { config } from 'mdye';

function MultiTableDashboard() {
  const [customers, setCustomers] = useState([]);
  const [orderStats, setOrderStats] = useState({});
  const [products, setProducts] = useState([]);
  const [statusOptions, setStatusOptions] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAllData();
  }, []);

  async function loadAllData() {
    try {
      setLoading(true);

      // 並行載入所有資料
      const [
        customersData,
        ordersData,
        productsData,
        optionSets
      ] = await Promise.all([
        // 1. 載入客戶資料
        getRecordList('CUSTOMER_WORKSHEET_ID', {
          pageSize: 10,
          sorts: [{ field: 'CREATE_TIME_FIELD_ID', isAsc: false }]
        }),

        // 2. 載入訂單統計（使用透視表API）
        getPivotData('ORDER_WORKSHEET_ID', {
          values: [
            {
              field: 'rowid',
              aggregation: 'COUNT',
              displayName: '訂單數量'
            },
            {
              field: 'AMOUNT_FIELD_ID',
              aggregation: 'SUM',
              displayName: '訂單總額'
            }
          ],
          rows: [
            {
              field: 'STATUS_FIELD_ID',
              displayName: '訂單狀態'
            }
          ]
        }),

        // 3. 載入熱銷產品
        getRecordList('PRODUCT_WORKSHEET_ID', {
          pageSize: 5,
          filter: {
            type: 'group',
            logic: 'AND',
            children: [{
              type: 'condition',
              field: 'HOT_SALE_FIELD_ID',
              operator: 'eq',
              value: ['1']
            }]
          }
        }),

        // 4. 載入選項集
        getOptionSets()
      ]);

      // 處理選項集資料
      const statusOptionSet = optionSets.find(
        opt => opt.name === '訂單狀態'
      );
      if (statusOptionSet) {
        const optionsMap = {};
        statusOptionSet.options.forEach(opt => {
          optionsMap[opt.key] = opt.value;
        });
        setStatusOptions(optionsMap);
      }

      setCustomers(customersData.rows);
      setOrderStats(ordersData);
      setProducts(productsData.rows);
    } catch (error) {
      console.error('載入資料失敗:', error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return <div className="loading">載入中...</div>;
  }

  return (
    <div className="multi-table-dashboard">
      {/* 訂單統計卡片 */}
      <section className="stats-section">
        <h2>訂單統計</h2>
        <div className="stats-grid">
          {orderStats.rows?.map(row => (
            <div key={row.value} className="stat-card">
              <h3>{statusOptions[row.value] || row.value}</h3>
              <p className="count">{row.COUNT}單</p>
              <p className="amount">¥{row.SUM?.toLocaleString()}</p>
            </div>
          ))}
        </div>
      </section>

      {/* 最新客戶 */}
      <section className="customers-section">
        <h2>最新客戶</h2>
        <div className="customer-list">
          {customers.map(customer => (
            <div key={customer.rowid} className="customer-card">
              <h4>{customer.NAME_FIELD_ID}</h4>
              <p>{customer.PHONE_FIELD_ID}</p>
            </div>
          ))}
        </div>
      </section>

      {/* 熱銷產品 */}
      <section className="products-section">
        <h2>熱銷產品</h2>
        <div className="product-grid">
          {products.map(product => (
            <div key={product.rowid} className="product-card">
              <img
                src={getImageUrl(product.IMAGE_FIELD_ID)}
                alt={product.NAME_FIELD_ID}
              />
              <h4>{product.NAME_FIELD_ID}</h4>
              <p className="price">¥{product.PRICE_FIELD_ID}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

// 輔助函式：取得圖片URL
function getImageUrl(attachments) {
  if (!attachments || attachments.length === 0) {
    return 'https://via.placeholder.com/200';
  }

  const files = typeof attachments === 'string'
    ? JSON.parse(attachments)
    : attachments;

  return files[0]?.url || 'https://via.placeholder.com/200';
}

export default MultiTableDashboard;
```

### 常用 V3 介面完整清單

#### 應用管理
- `GET /v3/app` - 取得應用資訊
- `POST /v3/app/worksheets/list` - 取得工作表清單
- `GET /v3/app/worksheets/{worksheet_id}` - 取得工作表詳情
- `GET /v3/app/worksheets/{worksheet_id}/structure` - 取得工作表結構

#### 資料查詢
- `POST /v3/app/worksheets/{worksheet_id}/rows/list` - 取得記錄清單（⭐最常用）
- `GET /v3/app/worksheets/{worksheet_id}/rows/{row_id}` - 取得單條記錄
- `POST /v3/app/worksheets/{worksheet_id}/rows/pivot` - 透視表統計（⭐推薦用於資料分析）

#### 資料操作
- `POST /v3/app/worksheets/{worksheet_id}/rows` - 建立記錄
- `PUT /v3/app/worksheets/{worksheet_id}/rows/{row_id}` - 更新記錄
- `DELETE /v3/app/worksheets/{worksheet_id}/rows/{row_id}` - 刪除記錄
- `POST /v3/app/worksheets/{worksheet_id}/rows/batch` - 批次建立
- `PUT /v3/app/worksheets/{worksheet_id}/rows/batch` - 批次更新

#### 選項集和角色
- `GET /v3/app/optionsets` - 取得選項集清單（⭐推薦用於統一狀態管理）
- `GET /v3/app/optionsets/{optionset_id}` - 取得選項集詳情
- `GET /v3/app/roles` - 取得角色清單
- `GET /v3/app/roles/{role_id}/members` - 取得角色成員

#### 工作流
- `GET /v3/app/workflows` - 取得工作流清單
- `POST /v3/app/workflows/{workflow_id}/trigger` - 觸發工作流

### 最佳實踐

#### 1. API 呼叫最佳化
```javascript
// ✅ 推薦：並行載入多個無依賴的資料
const [data1, data2, data3] = await Promise.all([
  getRecordList(worksheet1),
  getRecordList(worksheet2),
  getPivotData(worksheet3, config)
]);

// ❌ 避免：序列載入導致效能差
const data1 = await getRecordList(worksheet1);
const data2 = await getRecordList(worksheet2);
const data3 = await getPivotData(worksheet3, config);
```

#### 2. 錯誤處理
```javascript
try {
  const data = await getRecordList(worksheetId, options);
  setRecords(data.rows);
} catch (error) {
  console.error('載入失敗:', error);
  // 顯示友好錯誤提示
  if (error.message.includes('401')) {
    alert('認證失敗，請檢查 API 金鑰');
  } else {
    alert('載入失敗，請稍後重試');
  }
}
```

#### 3. 資料快取
```javascript
// 簡單的記憶體快取
const cache = new Map();

async function getCachedData(key, fetchFn, ttl = 5 * 60 * 1000) {
  const cached = cache.get(key);

  if (cached && Date.now() - cached.timestamp < ttl) {
    return cached.data;
  }

  const data = await fetchFn();
  cache.set(key, { data, timestamp: Date.now() });

  return data;
}

// 使用
const products = await getCachedData(
  'hot-products',
  () => getRecordList('PRODUCT_ID', { pageSize: 5 })
);
```

---

## 建置和釋出

### ⚠️ 重要：完整開發流程

**外掛開發完成後，必須執行建置和釋出步驟！**

完整的開發流程包括：
1. 本地開發（mdye start）
2. **建置專案（mdye build）** ⭐
3. **提交發布（mdye push）** ⭐

### 外掛釋出流程

#### 第1步：建置專案

執行以下命令將本地專案打包：

```bash
cd your_plugin_project
mdye build
```

**建置輸出示例：**
```
[21:20:33] 開始建置程式碼
ℹ Compiling Webpack
✔ Webpack: Compiled successfully in 1.94s
asset bundle.js 228 KiB [emitted] [minimized] (name: main)
webpack 5.98.0 compiled successfully in 1947 ms
[21:20:35] 建置程式碼完成
```

#### 第2步：提交併釋出

執行以下命令將本地專案提交併推送到線上：

```bash
mdye push -m "提交說明"
```

**提交說明編寫建議：**

建議在提交資訊中包含以下內容：
1. **功能特性**：列出外掛的主要功能
2. **技術實現**：說明關鍵技術點和最佳化
3. **版本說明**：首次釋出/功能更新/Bug修復

**完整示例：**

```bash
mdye push -m "訂單狀態檢視外掛首次釋出

功能特性:
- 按訂單狀態分類展示(待付款/已付款/已發貨/已完成/已取消)
- 完整訂單資訊展示(訂單編號/客戶/聯絡人/日期/金額/負責人)
- 多條關聯產品資訊展示(產品名稱/編號/分類/單價)
- 點選訂單卡片開啟原生行記錄彈窗
- 支援編輯/刪除訂單並自動重新整理清單
- 響應式網格佈局和流暢動畫效果

技術實現:
- 正確處理單選欄位(type 9)和關聯記錄欄位(type 29)
- 使用 getRowRelationRows API 處理多條關聯
- 使用 utils.openRecordInfo 實現原生互動
- Promise.all 並行載入提升效能"
```

#### 第3步：確認釋出成功

釋出成功後會顯示外掛資訊：

```
[21:20:54] 檔案上傳成功
[21:20:55] push成功
┌──────────────────────────────────────────────────────────┐
│  ---- 外掛資訊 ----                                       │
│                                                           │
│  外掛名稱: 自訂檢視                                     │
│  檢視名稱: 自訂檢視                                     │
│  檢視地址: https://www.mingdao.com/worksheet/...         │
│  提交資訊: 訂單狀態檢視外掛首次釋出                       │
│  提交人: 使用者名稱                                           │
└──────────────────────────────────────────────────────────┘
```

#### 釋出後的狀態

✅ **外掛已釋出** - 可以在組織內所有應用中使用
✅ **檢視地址** - 可以透過回傳的 URL 直接訪問外掛
✅ **組織共享** - 組織內其他成員可以使用該外掛

---

## BI 駕駛艙設計

### 什麼是 BI 駕駛艙？

BI 駕駛艙（Business Intelligence Dashboard）是從**業務分析師視角**設計的資料視覺化介面，而不是簡單的資料清單展示。

### BI 駕駛艙 vs 普通檢視的區別

**❌ 錯誤的駕駛艙設計（普通檢視思維）：**
- 只顯示當前工作表的記錄清單
- 簡單統計總數、今日新增
- 沒有業務邏輯，只是資料展示

**✅ 正確的 BI 駕駛艙設計（分析師思維）：**
- 展示跨表彙總的業務指標
- 顯示業務轉化漏斗（如銷售漏斗）
- 提供多維度趨勢分析
- 按業務模組組織資料


### 設計 BI 駕駛艙的思維流程

當使用者要求建立 BI 駕駛艙時，按以下步驟思考：

1. **分析業務場景**
   - 這是什麼型別的應用？（CRM/ERP/專案管理等）
   - 核心業務流程是什麼？
   - 管理層最關心哪些指標？

2. **確定指標維度**
   - 什麼是核心 KPI？（客戶數、銷售額、轉化率等）
   - 需要哪些時間維度？（今日/本週/本月/本季度）
   - 需要哪些分類維度？（按產品/按地區/按團隊等）

3. **設計資料展示**
   - 頂部：核心 KPI 卡片（4-6個）
   - 中部：業務流程分析（漏斗圖、趨勢圖）
   - 底部：詳細模組統計

4. **選擇視覺化方式**
   - 根據資料型別選擇合適的圖表
   - 保持視覺一致性（配色、字型、間距）
   - 突出重點資料

### 總結

設計 BI 駕駛艙的核心是：**從業務分析師的視角思考**，而不是從技術視角簡單展示資料。

- ✅ 展示業務指標，而不是原始資料
- ✅ 提供業務洞察，而不是資料清單
- ✅ 關注業務流程，而不是單表統計
- ✅ 支援決策分析，而不是查詢檢索

---

## 資料分析指標規範

### ⚠️ 核心原則：作為專業資料分析師，每一個指標都必須有明確的業務含義

在開發檢視外掛時，尤其是 BI 駕駛艙、資料看板等資料分析場景，**禁止**展示沒有明確業務含義的指標。

### 錯誤示例 ❌

```javascript
// ❌ 錯誤：只顯示數字，沒有說明這個數字代表什麼
<div className="metric-card">
  <div className="value">128</div>
</div>

// ❌ 錯誤：指標名稱模糊，不知道統計的是什麼
<div className="metric-card">
  <div className="title">數量</div>
  <div className="value">128</div>
</div>

// ❌ 錯誤：統計口徑不明確
<div className="metric-card">
  <div className="title">訂單</div>
  <div className="value">128</div>
  <div className="trend">+15%</div>  // 相比什麼時間段？
</div>
```

### 正確示例 ✅

```javascript
// ✅ 正確：完整的指標定義
<div className="metric-card">
  <div className="title">本月新增客戶數</div>
  <div className="value">128</div>
  <div className="description">
    2025年1月1日-1月13日新建的客戶記錄數量
  </div>
  <div className="trend">
    較上月同期（2024年12月1日-12月13日）增長 +15%
  </div>
</div>

// ✅ 正確：趨勢分析有明確的時間對比
<div className="chart-card">
  <h3>近7天訂單趨勢</h3>
  <div className="description">
    每日已完成狀態的訂單數量統計（2025-01-07 至 2025-01-13）
  </div>
  <LineChart data={dailyOrders} />
</div>

// ✅ 正確：轉化率指標有明確的計算公式
<div className="metric-card">
  <div className="title">客戶轉化率</div>
  <div className="value">32.5%</div>
  <div className="formula">
    已成交客戶數 ÷ 潛在客戶總數 = 41 ÷ 126
  </div>
  <div className="benchmark">
    行業平均：28% | 我們超出行業平均 +4.5%
  </div>
</div>
```

### 指標定義規範

#### 1. 數量統計類指標

**必須說明：**
- 統計物件是什麼？（客戶/訂單/產品等）
- 統計範圍是什麼？（全部/本月/本週/某個狀態）
- 統計條件是什麼？（已完成/待處理/某個分類）

**示例：**
```javascript
// ❌ 錯誤
總數：1,234

// ✅ 正確
本月已完成訂單總數：1,234
統計範圍：2025年1月1日-1月31日
統計條件：訂單狀態 = "已完成"
```

#### 2. 金額統計類指標

**必須說明：**
- 金額型別（銷售額/回款/利潤/成本）
- 統計週期（本月/本季度/本年）
- 幣種和單位（CNY 萬元/USD 千元）

**示例：**
```javascript
// ❌ 錯誤
銷售額：¥1,234,567

// ✅ 正確
本月銷售額：¥123.46 萬元
統計範圍：2025年1月1日-1月31日
統計口徑：已完成訂單的訂單金額彙總
目標達成率：82.3%（目標 ¥150 萬元）
```

#### 3. 比率/百分比類指標

**必須說明：**
- 分子是什麼？（已完成數量）
- 分母是什麼？（總數量）
- 計算公式（分子 ÷ 分母）

**示例：**
```javascript
// ❌ 錯誤
完成率：75%

// ✅ 正確
本月訂單完成率：75%
計算公式：已完成訂單數 ÷ 總訂單數 = 150 ÷ 200
統計範圍：2025年1月1日-1月31日
```

#### 4. 趨勢對比類指標

**必須說明：**
- 當前值是什麼？
- 對比基準是什麼？（上月/去年同期/上週）
- 增長率的計算方式

**示例：**
```javascript
// ❌ 錯誤
訂單數：150 ↑ +20%

// ✅ 正確
本月訂單數：150
對比上月：125（2024年12月）
環比增長：+20% [（150-125）÷ 125]
對比去年同期：130（2024年1月）
同比增長：+15.4% [（150-130）÷ 130]
```

#### 5. 排名/Top 類指標

**必須說明：**
- 排名依據是什麼？（銷售額/數量/增長率）
- 排名範圍是什麼？（全部產品/本區域/本部門）
- 統計週期是什麼？（本月/本季度）

**示例：**
```javascript
// ❌ 錯誤
Top 5 產品

// ✅ 正確
本月銷售額 Top 5 產品
排名依據：已完成訂單的產品銷售額彙總
統計範圍：2025年1月1日-1月31日
總產品數：156 款

1. 產品A：¥45.2萬元（佔比 36.6%）
2. 產品B：¥32.8萬元（佔比 26.6%）
...
```

### 程式碼實現最佳實踐

#### 完整的指標卡片元件示例

```javascript
function MetricCard({
  title,              // 指標名稱
  value,              // 當前值
  unit,               // 單位
  description,        // 指標說明
  compareValue,       // 對比值
  compareLabel,       // 對比標籤（如"上月"）
  comparePercent,     // 對比百分比
  formula,            // 計算公式（可選）
  benchmark,          // 行業基準（可選）
  period              // 統計週期
}) {
  return (
    <div className="metric-card">
      {/* 指標標題 */}
      <div className="metric-header">
        <h3>{title}</h3>
        <Tooltip content={description}>
          <InfoIcon />
        </Tooltip>
      </div>

      {/* 當前值 */}
      <div className="metric-value">
        <span className="value">{value}</span>
        <span className="unit">{unit}</span>
      </div>

      {/* 統計週期 */}
      <div className="metric-period">
        {period}
      </div>

      {/* 對比資訊 */}
      {compareValue && (
        <div className="metric-compare">
          <span className="compare-label">{compareLabel}：</span>
          <span className="compare-value">{compareValue}</span>
          <span className={`compare-trend ${comparePercent > 0 ? 'up' : 'down'}`}>
            {comparePercent > 0 ? '↑' : '↓'} {Math.abs(comparePercent)}%
          </span>
        </div>
      )}

      {/* 計算公式（可選） */}
      {formula && (
        <div className="metric-formula">
          <small>{formula}</small>
        </div>
      )}

      {/* 行業基準（可選） */}
      {benchmark && (
        <div className="metric-benchmark">
          <small>行業平均：{benchmark}</small>
        </div>
      )}
    </div>
  );
}

// 使用示例
<MetricCard
  title="本月客戶轉化率"
  value="32.5"
  unit="%"
  description="潛在客戶轉化為成交客戶的比率，反映銷售團隊的轉化能力"
  compareValue="28.3"
  compareLabel="上月"
  comparePercent={14.8}
  formula="已成交客戶數 ÷ 潛在客戶總數 = 41 ÷ 126"
  benchmark="28%（超出 +4.5%）"
  period="2025年1月1日 - 1月13日"
/>
```

#### 圖表標題和說明示例

```javascript
function ChartCard({ title, description, timeRange, data }) {
  return (
    <div className="chart-card">
      <div className="chart-header">
        <h3>{title}</h3>
        <div className="chart-description">
          {description}
        </div>
        <div className="chart-timerange">
          統計週期：{timeRange}
        </div>
      </div>

      <div className="chart-content">
        {/* 圖表內容 */}
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip
              formatter={(value, name) => [
                `${value} 單`,
                `訂單數量`
              ]}
            />
            <Bar dataKey="value" fill="#1890ff" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* 資料說明 */}
      <div className="chart-footer">
        <small>
          資料來源：訂單工作表 |
          統計條件：訂單狀態 = "已完成" |
          更新時間：{new Date().toLocaleString()}
        </small>
      </div>
    </div>
  );
}

// 使用示例
<ChartCard
  title="各地區銷售額分佈"
  description="按客戶所在省份統計已完成訂單的銷售額彙總，用於分析區域市場表現"
  timeRange="2025年1月1日 - 1月13日"
  data={regionSalesData}
/>
```

### 檢查清單：釋出前必須確認

在釋出檢視外掛前，使用以下清單檢查每一個指標：

- [ ] 指標名稱清晰準確（避免"數量"、"總數"等模糊詞彙）
- [ ] 有明確的統計範圍說明（時間/狀態/分類）
- [ ] 有明確的統計口徑說明（計算方式/篩選條件）
- [ ] 趨勢對比有明確的基準說明（對比什麼/增長率如何計算）
- [ ] 百分比指標有明確的分子分母說明
- [ ] 金額類指標有明確的幣種和單位
- [ ] 圖表有完整的標題、座標軸標籤和圖例
- [ ] 關鍵指標有業務含義說明（Tooltip 或描述文字）
- [ ] 資料更新時間清晰可見
- [ ] 資料來源和統計條件有說明

### 總結

作為專業的資料分析師，在開發檢視外掛時必須確保：

1. **每個數字都要有含義** - 不能只顯示數字，要說明這個數字代表什麼
2. **每個指標都要有定義** - 明確統計物件、範圍、條件、口徑
3. **每個趨勢都要有基準** - 增長/下降相比什麼時間段
4. **每個比率都要有說明** - 分子和分母分別是什麼
5. **每個圖表都要有標註** - 標題、座標軸、圖例、資料來源

只有這樣，使用者才能真正理解資料、分析業務、做出決策。

**記住：資料展示不是目的，幫助使用者理解業務、發現問題、做出決策才是目的。**

---

## 開發除錯問題排查

### 問題：使用者無法預覽外掛

當使用者反饋"回傳外掛預覽不了"或"看不到效果"時，按以下步驟排查：

#### 1. 檢查開發伺服器是否啟動

**症狀：**
- niio後臺顯示"載入失敗"
- 瀏覽器控制檯報錯：`net::ERR_CONNECTION_REFUSED`
- 檢視區域一片空白

**排查步驟：**

```bash
# 檢查開發伺服器是否在執行
ps aux | grep "mdye start"

# 如果沒有輸出，說明伺服器未啟動，執行：
cd view-plugin
mdye start
```

**預期結果：**
```
[21:20:33] 開始編譯程式碼
✔ Webpack: Compiled successfully in 1.94s
[21:20:35] 編譯完成，服務執行在：
http://localhost:3000/bundle.js
```

#### 2. 檢查埠是否被佔用

**症狀：**
- 執行 `mdye start` 時報錯
- 錯誤資訊包含 `EADDRINUSE` 或 `port already in use`

**排查步驟：**

```bash
# macOS/Linux：檢查 3000 埠占用情況
lsof -i :3000

# 如果埠被佔用，有兩種解決方案：

# 方案1：結束佔用埠的程序（推薦）
kill -9 <PID>  # PID 是上一步查到的程序 ID

# 方案2：使用其他埠
# 編輯 mdye.config.js，修改埠號：
{
  devServer: {
    port: 3001  // 改為其他未佔用的埠
  }
}
```

**Windows 排查：**
```cmd
# 檢查埠占用
netstat -ano | findstr :3000

# 結束程序
taskkill /PID <PID> /F
```

#### 3. 檢查防火牆設定

**症狀：**
- 本地瀏覽器能訪問 `http://localhost:3000/bundle.js`
- 但niio後臺預覽失敗

**排查步驟：**

```bash
# macOS：檢查防火牆狀態
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# 如果防火牆已開啟，臨時關閉測試（不推薦長期關閉）
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off

# 或者允許 Node.js 透過防火牆（推薦）
# 系統偏好設定 → 安全性與隱私 → 防火牆 → 防火牆選項
# 找到 Node.js，設定為"允許傳入連線"
```

#### 4. 檢查程式碼編譯錯誤

**症狀：**
- 伺服器啟動成功
- 但控制檯持續報錯
- 檢視顯示空白或錯誤資訊

**排查步驟：**

```bash
# 檢視開發伺服器的控制檯輸出
# 尋找以下關鍵詞：
# - "ERROR"：編譯錯誤
# - "WARNING"：警告資訊
# - "Syntax"：語法錯誤
# - "Cannot find module"：模組缺失

# 常見錯誤示例：
✗ ERROR in ./src/App.js
Module not found: Error: Can't resolve 'recharts' in '/path/to/project/src'

# 解決方法：安裝缺失的依賴
npm install recharts
```

#### 5. 檢查瀏覽器控制檯

**開啟方法：**
- Chrome/Edge：按 `F12` 或 `Cmd+Option+I`（macOS）
- 切換到 `Console` 標籤

**常見錯誤及解決：**

| 錯誤資訊 | 原因 | 解決方法 |
|---------|------|---------|
| `net::ERR_CONNECTION_REFUSED` | 開發伺服器未啟動 | 執行 `mdye start` |
| `Uncaught SyntaxError` | 程式碼語法錯誤 | 檢查程式碼，修復語法錯誤 |
| `Cannot read property of undefined` | 資料未正確載入 | 檢查 API 呼叫和資料處理 |
| `Mixed Content: blocked` | HTTP/HTTPS 混合內容 | 確保開發伺服器使用 HTTPS |

#### 6. 檢查niio後臺設定

**確認以下設定正確：**

1. **外掛除錯地址設定：**
   - 開啟niio → 應用 → 檢視外掛管理
   - 檢查除錯地址是否為：`http://localhost:3000/bundle.js`
   - 注意：埠號必須與開發伺服器一致

2. **瀏覽器快取清理：**
   - 按 `Cmd+Shift+R`（macOS）或 `Ctrl+Shift+R`（Windows）強制重新整理
   - 或清除瀏覽器快取後重試

3. **網路環境檢查：**
   - 確保本機與niio伺服器網路連通
   - 檢查是否使用了代理或 VPN

#### 7. 完整的啟動檢查清單

**在告訴使用者"已完成"前，確認：**

- [ ] `mdye start` 命令執行成功
- [ ] 控制檯顯示 `Compiled successfully`
- [ ] 訪問 `http://localhost:3000/bundle.js` 回傳正常內容（不是 404）
- [ ] 瀏覽器控制檯無報錯
- [ ] 3000 埠未被其他程序佔用
- [ ] 防火牆已允許 Node.js 連線（如果適用）
- [ ] niio後臺除錯地址設定正確

### 快速診斷命令

提供給使用者一鍵診斷指令碼：

```bash
#!/bin/bash
echo "=== niio 檢視外掛開發環境診斷 ==="
echo ""

# 1. 檢查 Node.js 版本
echo "1. Node.js 版本："
node --version || echo "❌ Node.js 未安裝"
echo ""

# 2. 檢查 mdye-cli 是否安裝
echo "2. mdye-cli 版本："
mdye --version || echo "❌ mdye-cli 未安裝"
echo ""

# 3. 檢查當前目錄
echo "3. 當前目錄："
pwd
echo ""

# 4. 檢查專案檔案
echo "4. 專案檔案檢查："
if [ -f "package.json" ]; then
  echo "✓ package.json 存在"
else
  echo "❌ package.json 不存在，請在專案根目錄執行"
fi

if [ -f "src/App.js" ] || [ -f "src/App.jsx" ]; then
  echo "✓ App 檔案存在"
else
  echo "❌ App 檔案不存在"
fi
echo ""

# 5. 檢查埠占用
echo "5. 檢查 3000 埠："
if lsof -i :3000 > /dev/null 2>&1; then
  echo "⚠️  3000 埠已被佔用："
  lsof -i :3000
else
  echo "✓ 3000 埠可用"
fi
echo ""

# 6. 檢查開發伺服器
echo "6. 檢查開發伺服器："
if ps aux | grep -v grep | grep "mdye start" > /dev/null; then
  echo "✓ 開發伺服器正在執行"
else
  echo "❌ 開發伺服器未執行"
fi
echo ""

echo "=== 診斷完成 ==="
```

**使用方法：**
```bash
# 儲存為 diagnose.sh
chmod +x diagnose.sh
./diagnose.sh
```

### 常見問題快速解決

#### 問題：伺服器啟動了但預覽空白

**可能原因：**
- 程式碼執行時錯誤
- API 呼叫失敗
- 資料載入超時

**解決步驟：**
1. 開啟瀏覽器控制檯，檢視錯誤資訊
2. 檢查 `config.appId`、`config.worksheetId` 等是否正確
3. 檢查 API 呼叫是否有錯誤提示
4. 確認工作表中有資料可供展示

#### 問題：修改程式碼後沒有變化

**可能原因：**
- 熱更新未生效
- 瀏覽器快取

**解決步驟：**
1. 檢查開發伺服器控制檯是否顯示 `Compiling...`
2. 強制重新整理瀏覽器（`Cmd+Shift+R` 或 `Ctrl+Shift+R`）
3. 重啟開發伺服器：
   ```bash
   # 停止伺服器（按 Ctrl+C）
   # 重新啟動
   mdye start
   ```

### 向使用者反饋的標準流程

當使用者報告"預覽不了"時，你應該：

1. **詢問具體症狀：**
   ```
   請問您遇到的具體情況是：
   1. niio後臺顯示"載入失敗"
   2. 顯示空白頁面
   3. 顯示錯誤資訊（請截圖）
   4. 其他情況
   ```

2. **執行基礎檢查：**
   ```bash
   # 檢查開發伺服器狀態
   ps aux | grep "mdye start"

   # 檢查埠占用
   lsof -i :3000
   ```

3. **提供解決方案：**
   - 如果伺服器未啟動 → 執行 `mdye start`
   - 如果埠被佔用 → 釋放埠或換埠
   - 如果有編譯錯誤 → 修復程式碼錯誤
   - 如果都正常 → 檢查瀏覽器控制檯

4. **確認問題解決：**
   ```
   現在請嘗試重新整理niio頁面，應該可以看到外掛效果了。
   如果還有問題，請提供：
   1. 瀏覽器控制檯的錯誤截圖
   2. 開發伺服器控制檯的輸出
   ```

---

## 常見問題

### 問題 1：選項欄位顯示 key 而不是文字

**問題描述:** 單選或多選欄位顯示的是 UUID 格式的 key,而不是選項的顯示文字。

**原因分析:**
1. niio選項欄位回傳的原始值是 JSON 格式的 key 陣列
2. 需要從 `config.controls` 中找到對應欄位的 `options`,然後根據 key 匹配出 value

**解決方案:**
```javascript
// 1. 取得欄位控制元件定義(包含options)
const control = config.controls.find(ctrl => ctrl.controlId === fieldId);

// 2. 解析選項欄位
function parseSingleSelect(value, control) {
  try {
    if (!value) return { key: "", text: "" };

    const keys = typeof value === 'string' ? JSON.parse(value) : value;
    const selectedKey = keys[0] || "";

    // 從 options 中查詢對應的顯示文字
    let selectedText = "";
    if (control && control.options) {
      const option = control.options.find(opt => opt.key === selectedKey);
      selectedText = option ? option.value : selectedKey;
    }

    return { key: selectedKey, text: selectedText };
  } catch (err) {
    console.error("解析單選欄位失敗:", err, value);
    return { key: "", text: "" };
  }
}
```

### 問題 2：找不到單選欄位

**問題描述:** 使用 `controls.find()` 查詢單選欄位時,回傳 `undefined`。

**原因分析:**
- 單選欄位的 type 是 **9** 而不是 11
- type 10 是多選,type 11 是下拉
- 如果只檢查 `ctrl.type === 11`,會遺漏 type 9 的單選欄位

**解決方案:**
```javascript
// ✅ 正確:包含所有選項欄位型別
const selectField = controls?.find(ctrl =>
  ctrl.controlName?.includes('狀態') &&
  (ctrl.type === 9 || ctrl.type === 10 || ctrl.type === 11)
);

// ❌ 錯誤:會遺漏 type 9
const selectField = controls?.find(ctrl =>
  ctrl.controlName?.includes('狀態') &&
  (ctrl.type === 10 || ctrl.type === 11)
);
```

### 問題 3：多條關聯欄位只顯示數字

**問題描述:** 關聯欄位顯示的是數字(如 `2`、`3`),而不是實際的關聯記錄資訊。

**原因分析:**
1. 多條關聯欄位 (enumDefault=2 或 subType=2) 回傳的原始值是數字,表示關聯記錄的數量
2. 與單條關聯不同,多條關聯不會直接回傳 JSON 陣列字串
3. 必須呼叫 `getRowRelationRows` API 才能取得實際的關聯記錄資料

**解決方案:**

```javascript
// 1. 判斷是否為多條關聯
function isMultipleRelation(value) {
  return typeof value === 'number' || (!isNaN(value) && value !== '');
}

// 2. 處理關聯欄位(支援單條和多條)
async function handleRelationField(worksheetId, controlId, rowId, fieldValue) {
  let relationData = [];

  if (isMultipleRelation(fieldValue)) {
    // 多條關聯:呼叫 API 取得詳情
    try {
      const result = await api.getRowRelationRows({
        worksheetId,
        controlId,
        rowId,
        pageSize: 100,
        pageIndex: 1
      });

      if (result && result.data) {
        relationData = result.data;
      }
    } catch (error) {
      console.error('取得多條關聯失敗:', error);
    }
  } else {
    // 單條關聯:直接解析
    relationData = parseRelationData(fieldValue);
  }

  return relationData;
}
```

### 問題 4：npm 安裝失敗
- 檢查網路連線
- 清理 npm 快取：`npm cache clean --force`
- 使用淘寶映象：`npm config set registry https://registry.npmmirror.com`

### 問題 5：mdye 命令不存在
- 重新安裝 mdye-cli
- 檢查 PATH 環境變數
- 使用 `which mdye` 檢查安裝位置

### 問題 6：專案啟動失敗
- 檢查埠是否被佔用
- 檢查依賴是否完整安裝
- 檢視錯誤日誌資訊

---

## 參考資源

### 官方文件
- [niio開發者文件](https://developers.mingdao.com/)
- [React 官方文件](https://react.dev/)
- [Node.js 官方文件](https://nodejs.org/)

### 技術社群
- niio開發者社群
- GitHub Issues

### 圖表庫
- [Recharts 圖表庫文件](https://recharts.org/)
- [Ant Design Charts](https://charts.ant.design/)

### 相關技能
- `hap-apiv3-data` - niio V3 介面完整文件

---

## 最佳實踐

### 1. 專案組織
- 保持專案結構清晰
- 合理劃分元件和模組
- 使用有意義的檔案命名

### 2. 程式碼質量
- 遵循 React 最佳實踐
- 使用 ESLint 和 Prettier
- 編寫清晰的註釋和文件

### 3. 效能最佳化
- 使用 React.memo 最佳化渲染
- 避免不必要的重渲染
- 最佳化狀態管理
- 使用程式碼分割

### 4. 安全注意事項
- 避免硬編碼敏感資訊
- 使用環境變數管理設定
- 驗證使用者輸入
- 防止 XSS 攻擊

### 5. 除錯技巧
- 使用瀏覽器開發者工具
- 檢視控制檯輸出
- 使用 React 開發者工具
- 新增除錯日誌

---

## 更新日誌

### v1.0.0 (2026-01-11)
- 初始版本釋出
- 整合完整的技能文件體系
- 包含專案初始化、API 使用、欄位處理、V3 整合等全流程
- 提供詳細的示例程式碼和最佳實踐
- 新增 BI 駕駛艙設計指南
- 包含完整的常見問題解決方案

---

**注意：** 此文件是 niio 檢視外掛開發 Agent 的完整技能包，包含了從專案建立到釋出的全流程指導。實際開發中請根據具體需求調整設定和程式碼。

**版權資訊：**
- 文件基於niio niio V3 API
- 適用於 mdye-cli beta-0.0.37+
- 更新時間：2026-01-12
