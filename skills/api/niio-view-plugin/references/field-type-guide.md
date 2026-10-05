# niio 檢視外掛開發 - 欄位型別處理經驗總結

## 🎯 核心發現

在開發niio niio 自訂檢視外掛時,發現了一個**非常重要的欄位型別對映問題**:

### ⚠️ 關鍵問題:單選欄位的 type 是 9,不是 11!

**官方文件可能存在誤導:**
- 文件中可能暗示單選是 type 11
- 但實際上 **type 9 = 單選 (SingleSelect)**
- type 10 = 多選 (MultipleSelect)
- type 11 = 下拉 (Dropdown)

## 📋 完整欄位型別對照表

| Type | 欄位型別 | 說明 |
|------|---------|------|
| 2 | 文字框 | Text |
| 3 | 手機 | PhoneNumber |
| 4 | 座機 | LandlinePhone |
| 5 | 郵箱 | Email |
| 6 | 數值 | Number |
| 7 | 證件 | Certificate |
| 8 | 金額 | Currency |
| **9** | **單選** | **SingleSelect** ⚠️ |
| 10 | 多選 | MultipleSelect |
| 11 | 下拉 | Dropdown |
| 14 | 附件 | Attachment |
| 15 | 日期 | Date |
| 16 | 時間 | DateTime |
| 19/23/24 | 地區 | Region |
| 26 | 成員 | Collaborator |
| 27 | 部門 | Department |
| 28 | 等級 | Rating |
| 29 | 連線他表 | Relation |
| 36 | 檢查框 | Checkbox |
| 40 | 定位 | Location |
| 41 | 富文字 | RichText |
| 42 | 簽名 | Signature |
| 46 | 時間 | Time |
| 48 | 組織角色 | OrgRole |

## 🔧 實際應用場景

### 場景:按行業分組顯示客戶

**問題現象:**
- 程式碼查詢行業欄位時回傳 `undefined`
- 所有客戶都被歸入"未分類"
- 控制檯顯示 `行業欄位: undefined`

**錯誤程式碼:**
```javascript
// ❌ 只查詢 type 10 和 11,遺漏了 type 9
const industryField = controls?.find(ctrl =>
  ctrl.controlName?.includes('行業') && (ctrl.type === 10 || ctrl.type === 11)
);
```

**正確程式碼:**
```javascript
// ✅ 包含 type 9, 10, 11 所有選項欄位
const industryField = controls?.find(ctrl =>
  ctrl.controlName?.includes('行業') && (ctrl.type === 9 || ctrl.type === 10 || ctrl.type === 11)
);
```

## 💡 選項欄位值解析

### 資料格式

選項欄位回傳的原始值格式:
```javascript
// 原始值(JSON字串)
"[\"42ad38bf-d3e6-441f-a960-670e704abe4a\"]"

// 解析後
["42ad38bf-d3e6-441f-a960-670e704abe4a"]

// 這是選項的 key,需要從 options 中查詢對應的 value
```

### 完整解析函式

```javascript
// 解析單選欄位
function parseSingleSelect(value, control) {
  try {
    if (!value) return { key: "", text: "" };

    // 解析選項key值 - 支援多種格式
    let keys = [];
    if (typeof value === 'string') {
      try {
        keys = JSON.parse(value);
      } catch {
        keys = [value];
      }
    } else if (Array.isArray(value)) {
      keys = value;
    } else {
      keys = [value];
    }

    const selectedKey = keys[0] || "";

    // 從控制元件選項中查詢對應的文字值
    let selectedText = "";
    if (control && control.options) {
      const option = control.options.find(opt => opt.key === selectedKey);
      selectedText = option ? option.value : selectedKey; // 找不到時回傳key
    } else {
      selectedText = selectedKey;
    }

    return { key: selectedKey, text: selectedText };
  } catch (err) {
    console.error("解析單選欄位失敗:", err, value);
    return { key: "", text: "" };
  }
}

// 欄位型別對映
function getFieldTypeByControlType(controlType) {
  const typeMap = {
    2: 'text',           // 文字框
    3: 'phone',          // 手機
    4: 'phone',          // 座機
    5: 'email',          // 郵箱
    6: 'number',         // 數值
    7: 'certificate',    // 證件
    8: 'number',         // 金額
    9: 'select',         // 單選 ⚠️ 重要
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

// 通用欄位值取得函式
function getFieldValue(fieldId, record, controls) {
  if (!fieldId || !record) return null;
  const rawValue = record[fieldId];
  if (rawValue === undefined || rawValue === null) return null;

  // 取得欄位控制元件定義
  const control = controls?.find(ctrl => ctrl.controlId === fieldId);
  if (!control) return rawValue;

  // 根據控制元件型別進行處理
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

    case 'boolean':
      return rawValue === "1" || rawValue === 1 || rawValue === true;

    default:
      return rawValue;
  }
}
```

## 🐛 除錯技巧

### 1. 列印所有欄位資訊

```javascript
useEffect(() => {
  console.log('=== 所有欄位詳細資訊 ===');
  controls?.forEach((ctrl, index) => {
    console.log(`欄位${index}:`, {
      id: ctrl.controlId,
      name: ctrl.controlName,
      type: ctrl.type,
      hasOptions: !!ctrl.options,
      optionsCount: ctrl.options?.length || 0
    });
    if (ctrl.options && ctrl.options.length > 0) {
      console.log(`  選項:`, ctrl.options);
    }
  });
  console.log('=== 欄位資訊結束 ===');
}, [controls]);
```

### 2. 列印欄位解析過程

```javascript
// 取得原始值
const rawValue = record[fieldId];
console.log('原始值:', rawValue);

// 解析值
const parsedValue = getFieldValue(fieldId, record, controls);
console.log('解析值:', parsedValue);

// 最終顯示值
const displayValue = parsedValue?.text || parsedValue;
console.log('顯示值:', displayValue);
```

## ✅ 最佳實踐

1. **總是包含 type 9 查詢選項欄位**
   ```javascript
   // 查詢所有選項欄位
   (ctrl.type === 9 || ctrl.type === 10 || ctrl.type === 11)
   ```

2. **從 config.controls 取得欄位定義**
   ```javascript
   const control = config.controls.find(ctrl => ctrl.controlId === fieldId);
   ```

3. **使用 options 匹配顯示文字**
   ```javascript
   const option = control.options.find(opt => opt.key === selectedKey);
   const displayText = option ? option.value : selectedKey;
   ```

4. **容錯處理**
   ```javascript
   // 找不到時回傳 key 而不是空字串
   selectedText = option ? option.value : selectedKey;
   ```

## 📚 相關資源

- niio 檢視外掛開發文件
- niio API V3 文件
- 欄位型別完整清單

## 🎓 經驗教訓

1. **不要完全依賴文件** - 實際的欄位型別編號可能與文件不一致
2. **使用除錯日誌** - 列印所有欄位資訊有助於發現問題
3. **完整的型別對映** - 建立完整的 type 到欄位型別的對映表
4. **容錯處理** - 總是考慮找不到選項的情況

---

**更新時間:** 2026-01-01
**適用版本:** niio API V3
**開發環境:** mdye-cli beta-0.0.37
