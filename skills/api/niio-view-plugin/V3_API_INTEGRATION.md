> **部署設定**：API、MCP 與網站網址必須使用本次選定部署環境的已確認設定，三者可能不同，不得只依 MCP 網址推測 API 或網站位置。下方 `.example.invalid` 網址只是不可連線的佔位範例，執行前必須替換；未確認網址時先詢問，不得向佔位網址傳送憑證。圖片與附件只能使用使用者提供或已授權的素材網址。

# niio 檢視外掛中使用 V3 介面

本文件是 [niio-view-plugin](./SKILL.md) 技能的補充說明,介紹如何在檢視外掛中使用 niio V3 介面。

## 資料操作方式對比

niio 檢視外掛支援兩種資料操作方式:

### 1. 使用外掛函式和元件 (mdye API)

**適用場景:** 檢視外掛內的標準資料操作

**特點:**
- ✅ 已封裝好身分驗證與授權,開箱即用
- ✅ 自動處理權限和上下文
- ✅ 提供完整的 TypeScript 型別定義
- ✅ 與niio原生 UI 元件整合

**示例:**
```javascript
import { api, utils, config } from 'mdye';

// 取得資料
const result = await api.getFilterRows({ worksheetId, viewId });

// 開啟記錄詳情
await utils.openRecordInfo({ appId, worksheetId, viewId, recordId });
```

### 2. 使用 niio V3 介面 (REST API)

**適用場景:**
- 需要呼叫 mdye 未封裝的介面
- 獨立前端頁面開發
- 跨應用資料操作
- 自訂複雜業務邏輯

**特點:**
- ✅ 完整的 RESTful API
- ✅ 支援所有niio功能
- ✅ 可在任何環境使用(外掛/獨立頁面)
- ⚠️ 需要手動設定身分驗證與授權(Appkey & Sign)

## 在檢視外掛中使用 V3 介面

### 方案1: 使用 mdye 封裝的 api

推薦優先使用 `mdye` 提供的 API:

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

### 方案2: 直接呼叫 V3 介面

當需要呼叫 mdye 未封裝的介面時:

```javascript
// 設定身分驗證與授權資訊 (從 MCP 設定中取得)
const API_CONFIG = {
  appkey: '你的Appkey',
  sign: '你的Sign'
};

// 封裝請求函式
async function callV3API(endpoint, method = 'GET', body = null) {
  const headers = {
    'Content-Type': 'application/json',
    'HAP-Appkey': API_CONFIG.appkey,
    'HAP-Sign': API_CONFIG.sign
  };

  const options = {
    method,
    headers
  };

  if (body) {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(
    `https://niio-api.example.invalid${endpoint}`,
    options
  );

  return await response.json();
}

// 使用示例
const optionSets = await callV3API('/v3/app/optionsets', 'GET');
const roles = await callV3API('/v3/app/roles', 'GET');
```

## 常用 V3 介面

### 應用管理
- `GET /v3/app` - 取得應用資訊
- `POST /v3/app/worksheets/list` - 取得工作表清單
- `GET /v3/app/worksheets/{worksheet_id}` - 取得工作表詳情

### 資料查詢
- `POST /v3/app/worksheets/{worksheet_id}/rows/list` - 取得記錄清單
- `GET /v3/app/worksheets/{worksheet_id}/rows/{row_id}` - 取得記錄詳情
- `GET /v3/app/worksheets/{worksheet_id}/rows/{row_id}/relations/{field}` - 取得關聯記錄

### 資料操作
- `POST /v3/app/worksheets/{worksheet_id}/rows` - 建立記錄
- `PUT /v3/app/worksheets/{worksheet_id}/rows/{row_id}` - 更新記錄
- `DELETE /v3/app/worksheets/{worksheet_id}/rows/batch` - 刪除記錄

### 選項集和角色
- `GET /v3/app/optionsets` - 取得選項集清單
- `GET /v3/app/optionsets/{optionset_id}` - 取得選項集詳情
- `GET /v3/app/roles` - 取得角色清單
- `GET /v3/app/roles/{role_id}/members` - 取得角色成員

### 使用者和部門
- `POST /v3/users/lookup` - 查詢使用者
- `POST /v3/departments/lookup` - 查詢部門
- `GET /v3/regions` - 取得地區清單

## 取得身分驗證與授權金鑰

### 從 MCP 設定中提取

MCP 設定示例:
```json
{
  "niio-mcp-MEGA CRM": {
    "url": "https://niio-api.example.invalid/mcp?HAP-Appkey=你的Appkey&HAP-Sign=你的Sign",
    "type": "sse"
  }
}
```

提取出:
- **Appkey**: `你的Appkey`
- **Sign**: `你的Sign`

**重要:** 這套金鑰同時適用於:
- MCP 伺服器訪問
- V3 API 呼叫
- 檢視外掛開發

## 完整示例

### 示例1: 取得並展示選項集

```javascript
import React, { useState, useEffect } from 'react';
import { config } from 'mdye';

const API_CONFIG = {
  appkey: '你的Appkey',
  sign: '你的Sign'
};

function OptionSetList() {
  const [optionSets, setOptionSets] = useState([]);

  useEffect(() => {
    loadOptionSets();
  }, []);

  async function loadOptionSets() {
    const headers = {
      'Content-Type': 'application/json',
      'HAP-Appkey': API_CONFIG.appkey,
      'HAP-Sign': API_CONFIG.sign
    };

    const response = await fetch(
      'https://niio-api.example.invalid/v3/app/optionsets',
      { method: 'GET', headers }
    );

    const result = await response.json();
    setOptionSets(result.optionSets || []);
  }

  return (
    <div>
      <h2>選項集清單</h2>
      <ul>
        {optionSets.map(optionSet => (
          <li key={optionSet.optionSetId}>
            {optionSet.optionSetName}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default OptionSetList;
```

### 示例2: 跨應用資料查詢

```javascript
async function getWorksheetData(worksheetId) {
  const headers = {
    'Content-Type': 'application/json',
    'HAP-Appkey': API_CONFIG.appkey,
    'HAP-Sign': API_CONFIG.sign
  };

  // 取得工作表結構
  const structureResponse = await fetch(
    `https://niio-api.example.invalid/v3/app/worksheets/${worksheetId}`,
    { method: 'GET', headers }
  );
  const structure = await structureResponse.json();

  // 取得記錄清單
  const rowsResponse = await fetch(
    `https://niio-api.example.invalid/v3/app/worksheets/${worksheetId}/rows/list`,
    {
      method: 'POST',
      headers,
      body: JSON.stringify({
        pageIndex: 1,
        pageSize: 100
      })
    }
  );
  const { rows } = await rowsResponse.json();

  return {
    structure,
    rows
  };
}
```

## 選擇建議

1. **優先使用 mdye API**
   - 如果功能已封裝,優先使用以減少開發量
   - 享受自動身分驗證與授權和型別提示

2. **補充使用 V3 介面**
   - 當需要 mdye 未提供的功能時使用
   - 例如:選項集管理、角色管理、使用者查詢等

3. **獨立頁面開發**
   - 只能使用 V3 介面編排資料操作
   - 需要自行處理身分驗證與授權和錯誤

## 更多資源

- **完整 V3 介面文件**: 檢視 `niio-apiv3-data` 技能文件
- **篩選器使用規範**: 參考 `niio-apiv3-data` 技能中的篩選器章節
- **API 文件查詢**: 使用 Apifox MCP Server 查詢完整 API 結構

```json
{
  "HAP-應用API文件": {
    "command": "npx -y apifox-mcp-server@latest --site-id=5442569",
    "args": [],
    "env": {},
    "type": "stdio"
  }
}
```
