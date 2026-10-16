# niio 檢視外掛開發參考

安裝、初始化、工具差異與發布規則統一以 [主技能](../SKILL.md) 為準。此處是 SDK 範例契約，不是本次部署的驗證紀錄。變數 appId/worksheetId/viewId/fieldId 必須來自已確認的 config 或選定欄位；片段不是可獨立執行的完整應用。寫入、刪除、原生編輯視窗與發布只在使用者授權範圍內執行，不是預設驗收步驟。

不自行全域安裝、不猜目錄、不終止其他程序、不關閉防火牆或忽略 TLS。啟動時報告實際埠與狀態，不假定使用者已設定除錯入口。保留啟動程序的識別資訊，結束工作時按已授權生命週期停止自己的服務。

發現模組缺失時先核對 package.json、鎖檔及 Node 版本；使用專案內受控安裝，不清空共用快取或修改 registry。檢視空白時區分編譯錯誤、連線拒絕、混合內容、SDK 目標／權限及資料解析錯誤，保留去敏證據交維護者處理。

可直接匯入 scripts/field_values.mjs 作型別檢查。數值缺值回 null、無效值拋錯，不能當成 0；關聯筆數不可把 null、boolean、陣列當成數字。參考 API 片段的空陣列容錯適用畫面呈現，正式驗收須保留並判定錯誤，不能把失敗當成空表。

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
const fieldControl = controls?.find(control => control.controlId === fieldId);
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
      // 僅保存去敏事件類型，不列印資料或原始錯誤物件。

      // 根據操作型別處理
      switch (result.action) {
        case 'update':
          // 記錄被更新,重新整理資料
          // 僅保存去敏事件類型，不列印資料或原始錯誤物件。
          loadRecords(); // 重新載入資料
          break;
        case 'delete':
          // 記錄被刪除,重新整理清單
          // 僅保存去敏事件類型，不列印資料或原始錯誤物件。
          loadRecords(); // 重新載入資料
          break;
        case 'close':
          // 使用者關閉彈窗(無修改)
          // 僅保存去敏事件類型，不列印資料或原始錯誤物件。
          break;
      }
    }
  } catch (error) {
    // 僅保存去敏事件類型，不列印資料或原始錯誤物件。
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
    // 僅保存去敏事件類型，不列印資料或原始錯誤物件。
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
    // 僅保存去敏事件類型，不列印資料或原始錯誤物件。
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

以下為來源文件的型別參考；須核對當前 SDK controls，不代表本部署已驗證：
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
    // 僅保存去敏事件類型，不列印資料或原始錯誤物件。
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
    // 僅保存去敏事件類型，不列印資料或原始錯誤物件。
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
  return (typeof value === 'number' || (typeof value === 'string' && /^\d+$/.test(value)))
    && Number.isSafeInteger(Number(value)) && Number(value) >= 0;
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
    // 僅保存去敏事件類型，不列印資料或原始錯誤物件。
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
    const parsed = typeof value === 'string' ? JSON.parse(value) : value;
    if (!Array.isArray(parsed)) throw new TypeError('Expected array');
    return parsed;
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
    const parsed = typeof value === 'string' ? JSON.parse(value) : value;
    if (!Array.isArray(parsed)) throw new TypeError('Expected array');
    return parsed;
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
      if (rawValue == null || rawValue === '') return null;
      if (!['number', 'string'].includes(typeof rawValue) || !Number.isFinite(Number(rawValue))) throw new TypeError('Invalid numeric field');
      return Number(rawValue);

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

niio 檢視外掛支援兩種資料操作方式:

#### 1. 使用外掛內部函式和元件 (mdye API)

**適用場景:** 檢視外掛內的標準資料操作

**特點:**
- ✅ 已封裝好身分驗證與授權,開箱即用
- ✅ 自動處理權限和上下文
- ✅ 提供完整的 TypeScript 型別定義
- ✅ 與niio原生 UI 元件整合
- ⚠️ 僅限目前工作表和檢視的資料操作
- ⚠️ 部分高階功能未封裝

**推薦使用的內部函式:**
```javascript
import { api, utils, config, md_emitter } from 'mdye';

// 取得目前檢視資料
api.getFilterRows({ worksheetId, viewId });

// 開啟原生記錄詳情彈窗
utils.openRecordInfo({ appId, worksheetId, viewId, recordId });

// 取得工作表結構資訊
config.controls; // 欄位清單
```

#### 2. 使用 niio REST API

原生 SDK 未涵蓋的功能，請依 [資料整合指引](../V3_API_INTEGRATION.md) 建立具備使用者身分驗證與資料授權的後端。不得把應用密鑰放進瀏覽器；REST 能力及路由需在目標部署獨立確認。

## 部署與憑證前置檢查

- 分別確認 MCP、REST、CLI 與網站的目標網址（含部署路徑）；不得相互推導。只使用本次已確認的部署、組織及應用。
- MCP 憑證可用不代表 REST 或 CLI 可用；不得自動掃描編輯器設定、提取或轉用 MCP 憑證。已確認的來源可沿用；缺少 REST 憑證時只索取本機檔案路徑或環境變數名稱，不要求在聊天貼出密鑰。
- REST 路由、驗證方式及 API 版本須由該部署文件確認。範例僅供協定參考；第一次先做已授權的唯讀請求，禁止攜帶憑證跟隨重新導向。核對 HTTP 狀態、JSON Content-Type、業務成功及預期資料結構；404／HTML 不能判定憑證有效或無效，停止並回報。
- `Authorization` 依已確認格式原樣使用，不重複加 Bearer。`HAP-Appid`、`HAP-Appkey`、`HAP-Sign` 是協定名稱，不做品牌替換；實際必要標頭依部署文件。
- API 密鑰只留在受控後端或本機環境，不寫入前端、版本庫、日誌或報告。前端使用原生 SDK 或具備使用者身分驗證與資料授權的後端；單純隱藏密鑰不等於限制資料存取。
- 查詢須限制應用、工作表、欄位與回傳量；不要把 `includeSystemFields=false` 當成欄位白名單。寫入依使用者已授權範圍執行並讀回；逾時或回應遺失先唯讀核對，不盲目重送。



## 指標與發布驗收

每個指標標示定義、範圍、篩選、時區、資料更新時間、幣別、分子／分母與比較基準；缺值與錯誤獨立顯示。僅載入第一頁不能宣稱全表總額；關聯讀取分頁並限制併發，避免無界 Promise.all。

使用 mock 測試空值、0、無效 JSON、未知選項、數字型別與目標不符。部署後先唯讀核對一筆合成資料；完成 build 不等於 push，push 不等於平台已發布或全組織可見。保留版本、目標檢視、發布結果與實際開啟證據；角色與同仁試用另行安排。
