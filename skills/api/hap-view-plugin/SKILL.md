---
name: hap-view-plugin
description: 建立和開發niio niio 自訂檢視外掛的技能。立即觸發條件：使用者提到"niio 檢視外掛"、"自訂檢視"、"mdye"、"檢視開發"、"外掛開發"、"初始化檢視專案"、"啟動檢視除錯"。提供完整的開發工作流程、API 使用指南和最佳實踐。
license: MIT
---

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

niio檢視外掛的 API 使用例項與最佳實踐，請參考本技能 `references/` 下的開發指南（如 `references/hap-view-plugin-dev-guide.md`）。

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
mdye init view --id 你的worksheetID-你的视图ID --template React
```

**參數說明：**
- `--id`: 外掛 ID（示例 ID，實際使用時需要替換）
- `--template React`: 使用 React 基礎示例模板

**專案結構：**
```
mdye_view_你的视图ID/
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
cd mdye_view_你的视图ID
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
// 使用辅助函数安全获取env中的配置项
function getEnvValue(env, key, defaultValue = null) {
  if (!env || !key) return defaultValue;

  const value = env[key];

  // 处理数组类型(字段选择器)
  if (Array.isArray(value)) {
    return value.length > 0 ? value[0] : defaultValue;
  }

  // 处理普通值
  return value !== undefined ? value : defaultValue;
}

// 使用示例
const titleFieldId = getEnvValue(env, 'title');
const maxRecords = getEnvValue(env, 'maxRecords', '50');
```

#### 1.2 取得 config 設定

```javascript
import { config } from "mdye";

// 获取应用、工作表、视图的ID
const { appId, worksheetId, viewId, controls } = config;

// 获取字段控件信息
const fieldControl = _.find(controls, { controlId: fieldId });
```

### 2. 資料取得 API

#### 2.1 取得工作表資料 (getFilterRows)

```javascript
import { api } from "mdye";

async function loadRecords() {
  const result = await api.getFilterRows({
    worksheetId,     // 必填-工作表ID
    viewId,          // 必填-视图ID
    pageIndex: 1,    // 可选-页码
    pageSize: 50,    // 可选-每页记录数
    sortId: "fieldId", // 可选-排序字段
    isAsc: true,     // 可选-升序排序
    // 获取关联字段数据
    requestParams: {
      plugin_detail_control: relationFieldId
    }
  });

  return result.data; // 记录数组
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
    controlId,       // 关联字段ID
    rowId,           // 主记录ID
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
        value: "测试文本"
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

// 打开记录详情
const handleRecordClick = async (recordId) => {
  try {
    const result = await utils.openRecordInfo({
      appId,
      worksheetId,
      viewId,
      recordId
    });

    // 处理返回结果
    if (result) {
      console.log('操作结果:', result);

      // 根据操作类型处理
      switch (result.action) {
        case 'update':
          // 记录被更新,刷新数据
          console.log('记录已更新:', result.value);
          loadRecords(); // 重新加载数据
          break;
        case 'delete':
          // 记录被删除,刷新列表
          console.log('记录已删除');
          loadRecords(); // 重新加载数据
          break;
        case 'close':
          // 用户关闭弹窗(无修改)
          console.log('用户关闭了弹窗');
          break;
      }
    }
  } catch (error) {
    console.error('打开记录详情失败:', error);
  }
};
```

**回傳值說明:**

```javascript
{
  action: 'update' | 'delete' | 'close',  // 操作类型
  value: object | null                     // 更新后的记录数据(仅 action='update' 时)
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

  // 加载记录列表
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
      console.error('加载记录失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 打开记录详情
  const handleRecordClick = async (recordId) => {
    try {
      const result = await utils.openRecordInfo({
        appId,
        worksheetId,
        viewId,
        recordId
      });

      // 自动刷新列表
      if (result?.action === 'update' || result?.action === 'delete') {
        loadRecords(); // 刷新数据
      }
    } catch (error) {
      console.error('打开记录详情失败:', error);
    }
  };

  // 初始加载
  useEffect(() => {
    loadRecords();
  }, []);

  return (
    <div>
      {loading ? (
        <div>加载中...</div>
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
// 1. 使用 useCallback 避免重复创建函数
const handleRecordClick = useCallback(async (recordId) => {
  const result = await utils.openRecordInfo({
    appId, worksheetId, viewId, recordId
  });
  if (result?.action === 'update' || result?.action === 'delete') {
    loadRecords();
  }
}, [appId, worksheetId, viewId]);

// 2. 只在需要时刷新
const handleRecordClick = async (recordId) => {
  const result = await utils.openRecordInfo({
    appId, worksheetId, viewId, recordId
  });

  // 根据具体操作决定是否刷新
  if (result?.action === 'update') {
    // 局部更新(性能更好)
    setRecords(prev =>
      prev.map(r => r.rowid === recordId ? result.value : r)
    );
  } else if (result?.action === 'delete') {
    // 从列表中移除
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
  unique: false  // 是否单选
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
    console.log('筛选条件已更新:', newFilters);
    // 重新获取数据
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
    console.log('新增记录:', newRecord);
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
// 只查找 type 10 和 11,会遗漏 type 9 的单选字段
const selectField = controls?.find(ctrl =>
  ctrl.controlName?.includes('状态') && (ctrl.type === 10 || ctrl.type === 11)
);
```

✅ **正確寫法:**
```javascript
// 包含 type 9, 10, 11 所有选项字段类型
const selectField = controls?.find(ctrl =>
  ctrl.controlName?.includes('状态') && (ctrl.type === 9 || ctrl.type === 10 || ctrl.type === 11)
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
    console.error("解析单选字段失败:", err);
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
    console.error("解析多选字段失败:", err);
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
   - 示例: `"[{\"sid\":\"...\",\"name\":\"客户名称\",\"sourcevalue\":\"...\"}]"`
   - 處理方式: 直接解析 JSON 字串即可

2. **多條關聯** (enumDefault=2 或 subType=2)
   - 回傳格式: 數字(表示關聯記錄的數量)
   - 示例: `2` (表示關聯了 2 條記錄)
   - 處理方式: **必須呼叫 `getRowRelationRows` API** 才能取得實際資料

**完整處理示例:**

```javascript
// 1. 判断是否为多条关联
function isMultipleRelation(value) {
  return typeof value === 'number' || (!isNaN(value) && value !== '');
}

// 2. 解析单条关联数据
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
          console.error("解析sourcevalue失败:", e);
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
    console.error("解析关联记录字段失败:", err);
    return [];
  }
}

// 3. 完整使用示例（包含单条和多条处理）
async function loadOrdersWithProducts() {
  const result = await api.getFilterRows({
    worksheetId,
    viewId,
    pageSize: 1000,
    pageIndex: 1
  });

  // 使用 Promise.all 并行处理所有订单
  const ordersData = await Promise.all(
    result.data.map(async (row) => {
      // 获取关联产品字段值
      const productsValue = row['relationFieldId'];
      let products = [];

      // 判断是单条还是多条关联
      if (isMultipleRelation(productsValue)) {
        // 多条关联:调用 API 获取详情
        try {
          const relationResult = await api.getRowRelationRows({
            worksheetId,
            controlId: 'relationFieldId',  // 关联字段ID
            rowId: row.rowid,
            pageSize: 100,
            pageIndex: 1
          });

          if (relationResult && relationResult.data) {
            products = relationResult.data.map(item => ({
              name: item['productNameFieldId'],    // 产品名称字段ID
              code: item['productCodeFieldId'],    // 产品编码字段ID
              price: item['productPriceFieldId'],  // 产品单价字段ID
              rowid: item.rowid
            }));
          }
        } catch (error) {
          console.error('获取多条关联失败:', error);
        }
      } else {
        // 单条关联:直接解析
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
// 在 config.controls 中查看关联字段配置
const relationControl = controls.find(ctrl => ctrl.controlId === 'relationFieldId');

// 单条关联配置
{
  "controlId": "示例控件ID",
  "type": 29,
  "controlName": "关联客户",
  "enumDefault": 1,  // 或 subType: 1
  // ... 其他属性
}

// 多条关联配置
{
  "controlId": "示例控件ID2",
  "type": 29,
  "controlName": "关联产品",
  "enumDefault": 2,  // 或 subType: 2
  // ... 其他属性
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
    2: 'text',           // 文本框
    3: 'phone',          // 手机
    4: 'phone',          // 座机
    5: 'email',          // 邮箱
    6: 'number',         // 数值
    7: 'certificate',    // 证件
    8: 'number',         // 金额
    9: 'select',         // 单选 ⚠️ 重要:type 9 是单选
    10: 'multiselect',   // 多选
    11: 'select',        // 下拉
    14: 'attachment',    // 附件
    15: 'date',          // 日期
    16: 'datetime',      // 时间
    19: 'region',        // 地区
    23: 'region',        // 地区
    24: 'region',        // 地区
    26: 'user',          // 成员
    27: 'department',    // 部门
    28: 'rating',        // 等级
    29: 'relation',      // 连接他表
    36: 'boolean',       // 检查框
    40: 'location',      // 定位
    41: 'richtext',      // 富文本
    42: 'signature',     // 签名
    46: 'time',          // 时间
    48: 'role',          // 组织角色
  };
  return typeMap[controlType] || 'unknown';
}
```

## mdye 命令列工具

### 基本命令

```bash
# 查看版本
mdye --version

# 授权登录
mdye auth

# 初始化项目
mdye init view --id <id> --template <template-name>

# 启动开发
mdye start

# 构建项目
mdye build

# 提交插件
mdye push -m "提交说明"

# 查看当前用户
mdye whoami

# 注销
mdye logout

# 同步插件参数配置
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
[21:20:33] 开始构建代码
ℹ Compiling Webpack
✔ Webpack: Compiled successfully in 1.94s
asset bundle.js 228 KiB [emitted] [minimized] (name: main)
webpack 5.98.0 compiled successfully in 1947 ms
[21:20:35] 构建代码完成
```

#### 第2步：提交併釋出

執行以下命令將本地專案提交併推送到線上待發布外掛清單：

```bash
mdye push -m "提交说明"
```

**提交說明編寫建議：**

建議在提交資訊中包含以下內容：
1. **功能特性**：列出外掛的主要功能
2. **技術實現**：說明關鍵技術點和最佳化
3. **版本說明**：首次釋出/功能更新/Bug修復

**完整示例：**

```bash
mdye push -m "订单状态视图插件首次发布

功能特性:
- 按订单状态分类展示(待付款/已付款/已发货/已完成/已取消)
- 完整订单信息展示(订单编号/客户/联系人/日期/金额/负责人)
- 多条关联产品信息展示(产品名称/编号/分类/单价)
- 点击订单卡片打开原生行记录弹窗
- 支持编辑/删除订单并自动刷新列表
- 响应式网格布局和流畅动画效果

技术实现:
- 正确处理单选字段(type 9)和关联记录字段(type 29)
- 使用 getRowRelationRows API 处理多条关联
- 使用 utils.openRecordInfo 实现原生交互
- Promise.all 并行加载提升性能"
```

#### 第3步：登入認證

提交時需要登入賬戶，按提示輸入：
- 使用者名稱（手機號或郵箱地址）
- 密碼

如果已登入，可以透過 `mdye whoami` 檢視當前登入使用者。

#### 第4步：確認釋出成功

釋出成功後會顯示外掛資訊：

```
[21:20:54] 文件上传成功
[21:20:55] push成功
┌──────────────────────────────────────────────────────────┐
│  ---- 插件信息 ----                                       │
│                                                           │
│  插件名称: 自定义视图                                     │
│  视图名称: 自定义视图                                     │
│  视图地址: https://www.mingdao.com/worksheet/...         │
│  提交信息: 订单状态视图插件首次发布                       │
│  提交人: 用户名                                           │
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
├── .config/          # 配置文件目录
├── src/              # 源代码目录
│   ├── components/   # 组件目录
│   ├── utils/        # 工具函数目录
│   ├── App.js        # 主应用组件
│   ├── index.js      # 入口文件
│   └── style.less    # 样式文件
├── mdye.json         # 插件配置文件
└── package.json      # 项目依赖配置
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
// 1. 获取字段控件定义(包含options)
const control = config.controls.find(ctrl => ctrl.controlId === fieldId);

// 2. 解析选项字段
function parseSingleSelect(value, control) {
  try {
    if (!value) return { key: "", text: "" };

    // 解析 JSON 字符串得到 key 数组
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

    // 从 options 中查找对应的显示文本
    let selectedText = "";
    if (control && control.options) {
      const option = control.options.find(opt => opt.key === selectedKey);
      selectedText = option ? option.value : selectedKey;
    }

    return { key: selectedKey, text: selectedText };
  } catch (err) {
    console.error("解析单选字段失败:", err, value);
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
// ✅ 正确:包含所有选项字段类型
const selectField = controls?.find(ctrl =>
  ctrl.controlName?.includes('状态') &&
  (ctrl.type === 9 || ctrl.type === 10 || ctrl.type === 11)
);

// ❌ 错误:会遗漏 type 9
const selectField = controls?.find(ctrl =>
  ctrl.controlName?.includes('状态') &&
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
// 1. 判断是否为多条关联
function isMultipleRelation(value) {
  return typeof value === 'number' || (!isNaN(value) && value !== '');
}

// 2. 处理关联字段(支持单条和多条)
async function handleRelationField(worksheetId, controlId, rowId, fieldValue) {
  let relationData = [];

  if (isMultipleRelation(fieldValue)) {
    // 多条关联:调用 API 获取详情
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
          name: item['titleFieldId'],  // 使用实际的标题字段ID
          // 解析其他需要的字段
        }));
      }
    } catch (error) {
      console.error('获取多条关联失败:', error);
    }
  } else {
    // 单条关联:直接解析
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

  // 使用 Promise.all 并行处理
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
// 方法1: 查看字段配置
const control = config.controls.find(ctrl => ctrl.controlId === 'relationFieldId');
if (control) {
  const isSingle = control.enumDefault === 1 || control.subType === 1;
  const isMultiple = control.enumDefault === 2 || control.subType === 2;
  console.log('单条关联:', isSingle, '多条关联:', isMultiple);
}

// 方法2: 根据返回值类型判断
const value = row['relationFieldId'];
if (typeof value === 'number' || !isNaN(value)) {
  console.log('这是多条关联,需要调用 getRowRelationRows');
} else if (typeof value === 'string') {
  console.log('这是单条关联,可以直接解析 JSON');
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
