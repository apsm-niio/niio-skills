---
name: niio-view-plugin
description: 建立和開發niio niio 自訂檢視外掛的技能。立即觸發條件：使用者提到"niio 檢視外掛"、"自訂檢視"、"mdye"、"檢視開發"、"外掛開發"、"初始化檢視專案"、"啟動檢視除錯"。提供完整的開發工作流程、API 使用指南和最佳實踐。
license: MIT
---
> **對外表達規範**：對使用者的說明、提示與成果摘要，統一使用 niio 品牌及台灣繁體中文。執行所需的技術名稱、套件、命令、API 參數與路徑請保留；只在操作或除錯所需的程式碼中呈現，勿將它們用作產品標題或品牌名稱。


# niio 自訂檢視外掛開發技能

此技能提供建立和開發niio niio 自訂檢視外掛的完整工作流程和開發規範。

## 關於此技能

此技能專門用於開發niio niio（High-performance Application Platform）自訂檢視外掛。透過整合的腳手架工具，可以快速建立 React 基礎示例模板專案，安裝依賴並啟動開發環境。

### 前置條件

在使用此技能前，確保：
1. 已安裝 16.20 或更高版本的 Node.js
2. 擁有niio開發者帳號和外掛開發權限
3. 瞭解基本的 React 開發知識

### 開發環境設定

#### 編輯器規則設定（可選）

可在檢視開發專案根目錄下建立 AI 編輯器規則檔案（按所用工具選擇，如 Cursor 的 `.cursorrules`、Claude Code 的 `CLAUDE.md` 等），寫入niio檢視外掛開發的程式碼規範與約定，即可在編輯器中獲得相應的智慧提示和規範檢查。具體規範可參考本技能 `references/` 下的開發指南。

#### 開發參考

niio檢視外掛的 API 使用例項與最佳實踐，請參考本技能 `references/` 下的開發指南（如 `references/niio-view-plugin-dev-guide.md`）。

### 核心功能

#### 1. 安裝 mdye-cli 工具
- 全域安裝外掛開發專用的命令列工具
- 驗證工具安裝是否成功

#### 2. 初始化本地專案
- 建立唯一的外掛專案資料夾
- 使用 React 基礎示例模板
- 生成專案設定檔案

#### 3. 安裝專案依賴
- 安裝專案所需的 npm 依賴包
- 設定開發環境

#### 4. 啟動開發環境
- 啟動本地開發伺服器
- 支援熱過載和即時預覽
- 提供線上除錯能力

## 開發工作流程

### 步驟 1：檢查並安裝 mdye-cli 工具

**首先檢查是否已安裝：**
```bash
mdye --version
```

如果顯示版本號，說明已安裝，可以跳過安裝步驟。

**如果未安裝，根據系統安裝：**

**Mac OS 使用者：**
```bash
sudo npm install -g mdye-cli
```

**Windows/Linux 使用者：**
```bash
npm install -g mdye-cli
```

**驗證安裝：**
```bash
mdye --version
```

### 步驟 2：初始化本地專案

**建立專案命令：**
```bash
mdye init view --id 你的worksheetID-你的檢視ID --template React
```

**參數說明：**
- `--id`: 外掛 ID（示例 ID，實際使用時需要替換）
- `--template React`: 使用 React 基礎示例模板

**專案結構：**
```
mdye_view_你的檢視ID/
├── package.json
├── mdye.json
├── src/
│   ├── index.jsx
│   ├── App.jsx
│   └── styles.less
└── .gitignore
```

### 步驟 3：進入專案目錄並安裝依賴

**進入專案目錄：**
```bash
cd mdye_view_你的檢視ID
```

**安裝依賴：**
```bash
npm i
```

### 步驟 4：啟動開發環境

**啟動命令：**
```bash
mdye start
```

**啟動後：**
- 開發伺服器將在 `http://localhost:3000/` 啟動
- 將除錯地址 `http://localhost:3000/bundle.js` 貼上到niio檢視設定開發除錯輸入框
- 支援即時編輯和熱過載

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

**回傳值說明:**

```javascript
{
  action: 'update' | 'delete' | 'close',  // 操作型別
  value: object | null                     // 更新後的記錄資料(僅 action='update' 時)
}
```

**完整的 React Hook 示例(包含自動重新整理):**

```javascript
import React, { useEffect, useState } from 'react';
import { config, api, utils } from 'mdye';

function RecordsList() {
  const { appId, worksheetId, viewId } = config;
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);

  // 載入記錄清單
  const loadRecords = async () => {
    try {
      setLoading(true);
      const result = await api.getFilterRows({
        worksheetId,
        viewId,
        pageSize: 100,
        pageIndex: 1
      });
      setRecords(result.data || []);
    } catch (error) {
      console.error('載入記錄失敗:', error);
    } finally {
      setLoading(false);
    }
  };

  // 開啟記錄詳情
  const handleRecordClick = async (recordId) => {
    try {
      const result = await utils.openRecordInfo({
        appId,
        worksheetId,
        viewId,
        recordId
      });

      // 自動重新整理清單
      if (result?.action === 'update' || result?.action === 'delete') {
        loadRecords(); // 重新整理資料
      }
    } catch (error) {
      console.error('開啟記錄詳情失敗:', error);
    }
  };

  // 初始載入
  useEffect(() => {
    loadRecords();
  }, []);

  return (
    <div>
      {loading ? (
        <div>載入中...</div>
      ) : (
        <div>
          {records.map(record => (
            <div
              key={record.rowid}
              onClick={() => handleRecordClick(record.rowid)}
              style={{ cursor: 'pointer' }}
            >
              {record.title}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

**效能最佳化建議:**

```javascript
// 1. 使用 useCallback 避免重複建立函式
const handleRecordClick = useCallback(async (recordId) => {
  const result = await utils.openRecordInfo({
    appId, worksheetId, viewId, recordId
  });
  if (result?.action === 'update' || result?.action === 'delete') {
    loadRecords();
  }
}, [appId, worksheetId, viewId]);

// 2. 只在需要時重新整理
const handleRecordClick = async (recordId) => {
  const result = await utils.openRecordInfo({
    appId, worksheetId, viewId, recordId
  });

  // 根據具體操作決定是否重新整理
  if (result?.action === 'update') {
    // 區域性更新(效能更好)
    setRecords(prev =>
      prev.map(r => r.rowid === recordId ? result.value : r)
    );
  } else if (result?.action === 'delete') {
    // 從清單中移除
    setRecords(prev => prev.filter(r => r.rowid !== recordId));
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

#### 4.4 選擇部門

```javascript
const departments = await utils.selectDepartments({
  projectId: "orgId1",
  unique: false
});
```

#### 4.5 選擇位置

```javascript
const location = await utils.selectLocation({
  distance: 1000,
  defaultPosition: { lat: 39.915, lng: 116.404 },
  multiple: false
});
```

#### 4.6 選擇記錄

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

## 特殊欄位型別處理

### ⚠️ 重要提示:欄位型別編號

**niio欄位型別編號與文件中的列舉值不完全一致,開發時務必注意:**

根據niio API V3 版本的實際欄位型別定義:
- **Type 9** = 單選 (SingleSelect) ⚠️ 注意不是 type 11
- **Type 10** = 多選 (MultipleSelect)
- **Type 11** = 下拉 (Dropdown)

### 完整欄位型別對照表(V3 實用版)

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
| 21 | DynamicLink | 自由連結 | ❌ | ✅ |
| 22 | Divider | 分段 | ❌ | ❌ |
| 25 | AmountInWords | 大寫金額 | ❌ | ✅ |
| 26 | Collaborator | 成員 | ✅ | ✅ |
| 27 | Department | 部門 | ❌ | ✅ |
| 28 | Rating | 等級 | ❌ | ✅ |
| 29 | Relation | 連線他表 | ✅ | ✅ |
| 30 | Lookup | 他表欄位 | ❌ | ✅ |
| 31 | Formula | 公式 | ❌ | ✅ |
| 32 | Concatenate | 文字拼接 | ❌ | ✅ |
| 33 | AutoNumber | 自動編號 | ❌ | ✅ |
| 34 | SubTable | 子表 | ❌ | ✅ |
| 35 | CascadingSelect | 級聯選擇 | ❌ | ✅ |
| 36 | Checkbox | 檢查框 | ❌ | ✅ |
| 37 | Rollup | 彙總 | ❌ | ✅ |
| 38 | DateFormula | 公式(日期) | ❌ | ✅ |
| 39 | CodeScan | 掃碼 | ❌ | ✅ |
| 40 | Location | 定位 | ❌ | ✅ |
| 41 | RichText | 富文字 | ❌ | ✅ |
| 42 | Signature | 簽名 | ❌ | ✅ |
| 43 | OCR | 文字識別 | ❌ | ✅ |
| 44 | Role | 角色 | ❌ | ✅ |
| 45 | Embed | 嵌入 | ❌ | ❌ |
| 46 | Time | 時間 | ✅ | ✅ |
| 47 | Barcode | 條碼 | ❌ | ✅ |
| 48 | OrgRole | 組織角色 | ❌ | ✅ |

### 常見錯誤示例

❌ **錯誤寫法:**
```javascript
// 只查詢 type 10 和 11,會遺漏 type 9 的單選欄位
const selectField = controls?.find(ctrl =>
  ctrl.controlName?.includes('狀態') && (ctrl.type === 10 || ctrl.type === 11)
);
```

✅ **正確寫法:**
```javascript
// 包含 type 9, 10, 11 所有選項欄位型別
const selectField = controls?.find(ctrl =>
  ctrl.controlName?.includes('狀態') && (ctrl.type === 9 || ctrl.type === 10 || ctrl.type === 11)
);
```

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

#### 定位欄位

```javascript
function parseLocation(value) {
  try {
    if (!value) return { title: "", address: "", x: 0, y: 0 };
    return typeof value === 'string' ? JSON.parse(value) : value;
  } catch (err) {
    return { title: "", address: "", x: 0, y: 0 };
  }
}
```

#### 關聯記錄欄位（⚠️ 重要！）

**關聯欄位 (type 29) 的特殊處理規則:**

關聯欄位根據 `enumDefault` 或 `subType` 屬性分為兩種型別,回傳資料格式完全不同:

1. **單條關聯** (enumDefault=1 或 subType=1)
   - 回傳格式: JSON 陣列字串
   - 示例: `"[{\"sid\":\"...\",\"name\":\"客戶名稱\",\"sourcevalue\":\"...\"}]"`
   - 處理方式: 直接解析 JSON 字串即可

2. **多條關聯** (enumDefault=2 或 subType=2)
   - 回傳格式: 數字(表示關聯記錄的數量)
   - 示例: `2` (表示關聯了 2 條記錄)
   - 處理方式: **必須呼叫 `getRowRelationRows` API** 才能取得實際資料

**完整處理示例:**

```javascript
// 1. 判斷是否為多條關聯
function isMultipleRelation(value) {
  return typeof value === 'number' || (!isNaN(value) && value !== '');
}

// 2. 解析單條關聯資料
function parseRelationData(value) {
  try {
    if (!value) return [];

    const relations = typeof value === 'string' ? JSON.parse(value) : value;
    if (!Array.isArray(relations)) return [];

    return relations.map(item => {
      let sourceValue = {};
      if (item.sourcevalue) {
        try {
          sourceValue = typeof item.sourcevalue === 'string'
            ? JSON.parse(item.sourcevalue)
            : item.sourcevalue;
        } catch (e) {
          console.error("解析sourcevalue失敗:", e);
        }
      }

      return {
        sid: item.sid || '',
        name: item.name || '',
        rowid: sourceValue.rowid || '',
        ...item
      };
    });
  } catch (err) {
    console.error("解析關聯記錄欄位失敗:", err);
    return [];
  }
}

// 3. 完整使用示例（包含單條和多條處理）
async function loadOrdersWithProducts() {
  const result = await api.getFilterRows({
    worksheetId,
    viewId,
    pageSize: 1000,
    pageIndex: 1
  });

  // 使用 Promise.all 並行處理所有訂單
  const ordersData = await Promise.all(
    result.data.map(async (row) => {
      // 取得關聯產品欄位值
      const productsValue = row['relationFieldId'];
      let products = [];

      // 判斷是單條還是多條關聯
      if (isMultipleRelation(productsValue)) {
        // 多條關聯:呼叫 API 取得詳情
        try {
          const relationResult = await api.getRowRelationRows({
            worksheetId,
            controlId: 'relationFieldId',  // 關聯欄位ID
            rowId: row.rowid,
            pageSize: 100,
            pageIndex: 1
          });

          if (relationResult && relationResult.data) {
            products = relationResult.data.map(item => ({
              name: item['productNameFieldId'],    // 產品名稱欄位ID
              code: item['productCodeFieldId'],    // 產品編碼欄位ID
              price: item['productPriceFieldId'],  // 產品單價欄位ID
              rowid: item.rowid
            }));
          }
        } catch (error) {
          console.error('取得多條關聯失敗:', error);
        }
      } else {
        // 單條關聯:直接解析
        products = parseRelationData(productsValue);
      }

      return {
        id: row.rowid,
        products: products,
        productsCount: isMultipleRelation(productsValue)
          ? Number(productsValue)
          : products.length
      };
    })
  );

  return ordersData;
}
```

**欄位設定示例:**

```javascript
// 在 config.controls 中檢視關聯欄位設定
const relationControl = controls.find(ctrl => ctrl.controlId === 'relationFieldId');

// 單條關聯設定
{
  "controlId": "示例控制元件ID",
  "type": 29,
  "controlName": "關聯客戶",
  "enumDefault": 1,  // 或 subType: 1
  // ... 其他屬性
}

// 多條關聯設定
{
  "controlId": "示例控制元件ID2",
  "type": 29,
  "controlName": "關聯產品",
  "enumDefault": 2,  // 或 subType: 2
  // ... 其他屬性
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

    case 'department':
      return parseDepartments(rawValue);

    case 'attachment':
      return parseAttachments(rawValue);

    case 'location':
      return parseLocation(rawValue);

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

## mdye 命令列工具

### 基本命令

```bash
# 檢視版本
mdye --version

# 授權登入
mdye auth

# 初始化專案
mdye init view --id <id> --template <template-name>

# 啟動開發
mdye start

# 建置專案
mdye build

# 提交外掛
mdye push -m "提交說明"

# 檢視目前使用者
mdye whoami

# 登出
mdye logout

# 同步外掛參數設定
mdye sync-params -f <file-path>
```

### 外掛釋出流程（重要！）

外掛開發完成後，需要按以下步驟提交發布到niio平台。釋出成功後，本外掛在組織下所有應用均可使用。

#### 第1步：建置專案

執行以下命令將本地專案打包：

```bash
cd your_plugin_project
mdye build
```

**建置過程說明：**
- Webpack 會編譯並打包所有原始碼
- 生成最佳化後的 `bundle.js` 檔案
- 通常需要 1-2 秒完成編譯
- 成功後會顯示 "建置程式碼完成" 和 bundle 檔案大小

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

執行以下命令將本地專案提交併推送到線上待發布外掛清單：

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

#### 第3步：登入認證

提交時需要登入賬戶，按提示輸入：
- 使用者名稱（手機號或郵箱地址）
- 密碼

如果已登入，可以透過 `mdye whoami` 檢視目前登入使用者。

#### 第4步：確認釋出成功

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

#### 常見問題

**問題1: 建置失敗**
- 檢查程式碼語法錯誤
- 確保所有依賴已正確安裝 (`npm install`)
- 檢視錯誤日誌定位問題

**問題2: 推送失敗**
- 確認已登入：`mdye whoami`
- 檢查網路連線
- 驗證帳號權限是否支援外掛開發

**問題3: 登入超時**
- 重新登入：`mdye auth`
- 輸入正確的手機號/郵箱和密碼

### 本地專案結構

```
plugin_project/
├── .config/          # 設定檔案目錄
├── src/              # 原始碼目錄
│   ├── components/   # 元件目錄
│   ├── utils/        # 工具函式目錄
│   ├── App.js        # 主應用元件
│   ├── index.js      # 入口檔案
│   └── style.less    # 樣式檔案
├── mdye.json         # 外掛設定檔案
└── package.json      # 專案依賴設定
```

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

## 常見問題解決

### 問題 1：選項欄位顯示 key 而不是文字

**問題描述:** 單選或多選欄位顯示的是 UUID 格式的 key (如 `42ad38bf-d3e6-441f-a960-670e704abe4a`),而不是選項的顯示文字。

**原因分析:**
1. niio選項欄位回傳的原始值是 JSON 格式的 key 陣列,如 `"[\"42ad38bf-d3e6-441f-a960-670e704abe4a\"]"`
2. 需要從 `config.controls` 中找到對應欄位的 `options`,然後根據 key 匹配出 value

**解決方案:**
```javascript
// 1. 取得欄位控制元件定義(包含options)
const control = config.controls.find(ctrl => ctrl.controlId === fieldId);

// 2. 解析選項欄位
function parseSingleSelect(value, control) {
  try {
    if (!value) return { key: "", text: "" };

    // 解析 JSON 字串得到 key 陣列
    let keys = [];
    if (typeof value === 'string') {
      try {
        keys = JSON.parse(value); // ["42ad38bf-..."]
      } catch {
        keys = [value];
      }
    } else if (Array.isArray(value)) {
      keys = value;
    }

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
        relationData = result.data.map(item => ({
          rowid: item.rowid,
          name: item['titleFieldId'],  // 使用實際的標題欄位ID
          // 解析其他需要的欄位
        }));
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

// 3. 完整使用示例
async function loadRecordsWithRelations() {
  const result = await api.getFilterRows({
    worksheetId,
    viewId,
    pageSize: 100,
    pageIndex: 1
  });

  // 使用 Promise.all 並行處理
  const records = await Promise.all(
    result.data.map(async (row) => {
      const relationValue = row['relationFieldId'];

      const relations = await handleRelationField(
        worksheetId,
        'relationFieldId',
        row.rowid,
        relationValue
      );

      return {
        ...row,
        relations: relations
      };
    })
  );

  return records;
}
```

**如何判斷欄位是單條還是多條關聯:**

```javascript
// 方法1: 檢視欄位設定
const control = config.controls.find(ctrl => ctrl.controlId === 'relationFieldId');
if (control) {
  const isSingle = control.enumDefault === 1 || control.subType === 1;
  const isMultiple = control.enumDefault === 2 || control.subType === 2;
  console.log('單條關聯:', isSingle, '多條關聯:', isMultiple);
}

// 方法2: 根據回傳值型別判斷
const value = row['relationFieldId'];
if (typeof value === 'number' || !isNaN(value)) {
  console.log('這是多條關聯,需要呼叫 getRowRelationRows');
} else if (typeof value === 'string') {
  console.log('這是單條關聯,可以直接解析 JSON');
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

### 問題 7：外掛 ID 衝突
- 使用新的唯一字尾
- 刪除舊的衝突專案
- 重新初始化專案

## 參考資源

- niio開發者文件
- React 官方文件
- Node.js 官方文件
- niio開發者社群

---

**注意：** 此技能提供的是開發工作流程指導和 API 使用規範，實際開發中請根據具體需求調整設定和程式碼。
