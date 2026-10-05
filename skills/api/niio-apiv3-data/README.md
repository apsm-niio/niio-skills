# niio V3 API 使用技能

## 簡介

這是一個專業的技能，用於使用niio niio V3 介面進行資料操作和頁面開發。提供完整的 API 使用指南、最佳實踐和常見問題解決方案。

## 適用場景

- ✅ 在自訂檢視外掛中呼叫 V3 介面操作資料
- ✅ 在獨立前端頁面中使用 V3 介面編排業務邏輯
- ✅ 即時取得和操作niio應用中的資料
- ✅ 資料遷移和批次操作
- ✅ 建置基於 niio 的完整應用

## 核心能力

1. **完整的 API 使用工作流**
   - 從零建置應用到資料操作的完整流程
   - 詳細的欄位型別處理規範
   - Filter 篩選器完整語法

2. **關聯欄位深度查詢**
   - 關聯欄位的建立和使用
   - 批次查詢最佳化（避免 N+1 問題）
   - 取得關聯記錄的完整資料

3. **常見陷阱和解決方案**
   - 選項欄位篩選必須使用 key（UUID）
   - 數值欄位篩選 value 必須是字串陣列
   - 關聯欄位使用 in 或 eq 運算子（value 為 rowid 陣列）

4. **效能最佳化最佳實踐**
   - 查詢最佳化建議
   - 批次操作最佳化
   - 關聯欄位最佳化

## 使用方法

當使用者提到以下關鍵詞時，會自動觸發此技能：

- "niio V3 介面"
- "niio API"
- "API 呼叫"
- "資料 API"
- "Appkey"
- "Sign"
- "介面身分驗證與授權"

## 核心文件

### 主要文件

- **`SKILL.md`** - 技能主文件
  - 快速開始指南
  - 核心工作流程
  - Filter 篩選器規範
  - 欄位型別處理規範
  - 常見陷阱與解決方案
  - 效能最佳化建議

- **`references/niio-api-usage-guide.md`** - niio V3 API 使用規範完整指南
  - 詳細的 API 使用流程（從零建置應用到資料操作）
  - 欄位型別參數詳解
  - 建立/更新記錄規範（triggerWorkflow 詳解）
  - 查詢篩選規範（Filter 物件結構、運算子清單）
  - 資料透視分析規範
  - 關聯欄位完整指南
  - 常見陷阱與解決方案
  - 效能最佳化建議
  - 最佳實踐總結

## 關鍵要點

### 1. 選項欄位篩選必須使用 key（UUID）

```javascript
// ❌ 錯誤
value: ["成交客戶"]  // 顯示文字

// ✅ 正確
value: ["74c7b607-864d-4cc4-b401-28acba2636e9"]  // 選項key
```

### 2. 數值欄位篩選 value 必須是字串陣列

```javascript
// ❌ 錯誤
value: [1000000]  // 數字型別

// ✅ 正確
value: ["1000000"]  // 字串陣列
```

### 3. 關聯欄位使用 in 或 eq 運算子

```javascript
// ❌ 錯誤
operator: "belongsto"  // V3 API 無 belongsto 運算子

// ✅ 正確
operator: "in"  // 關聯欄位用 in（多值）或 eq（單值），value 為 rowid 陣列
```

### 4. triggerWorkflow 參數

- `true` - 正常業務操作（預設）
- `false` - 資料遷移、批次初始化、測試資料

## 檔案結構

```
niio-apiv3-data/
├── SKILL.md                          # 技能主文件
├── README.md                          # 本檔案
└── references/
    └── niio-api-usage-guide.md         # niio V3 API 使用規範完整指南
```

## 參考資源

### 線上文件

- [API 整體介紹](https://apifox.mingdao.com/7271706m0.md)
- [欄位型別對照表](https://apifox.mingdao.com/7271709m0.md)
- [篩選器使用指南](https://apifox.mingdao.com/7271713m0.md)
- [錯誤碼說明](https://apifox.mingdao.com/7271715m0.md)

### 相關技能

- **niio 前後端專案建置指南** - 使用 niio 作為資料庫建置獨立網站
- **niio MCP 使用指南** - 瞭解如何使用 niio MCP 進行應用管理
- **niio 檢視外掛開發指南** - 開發 niio 自訂檢視外掛

## 版本資訊

- **技能版本**: v2.0
- **最後更新**: 2026-01-11
- **基於**: niio API V3
- **詳細規範**: 參考 `references/niio-api-usage-guide.md`
