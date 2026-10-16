# niio 檢視外掛欄位解析

型別以本次 SDK config.controls 為準。來源參考：2 文字、6 數值、8 金額、9 單選、10 多選、11 下拉、14 附件、15 日期、16 日期時間、26 成員、27 部門、29 關聯。不是本部署的完整支援清單；不要從欄位名稱猜 ID，也不要用 CLI schema 的型別取代 SDK 型別。

可執行的純函式位於 [field_values.mjs](../scripts/field_values.mjs)：

```javascript
import {parseArray, parseNumber, parseOptions, isRelationCount} from './scripts/field_values.mjs';
const zero = parseNumber('0'); // 0
const missing = parseNumber(''); // null
const selections = parseOptions('["mock-key"]', {options:[{key:'mock-key',value:'示例'}]});
const count = isRelationCount('2'); // true; null/false/[] 都是 false
```

parseArray 僅接受陣列或其 JSON 字串（空值回 []）；無效 JSON／物件拋錯。parseOptions 保留未知 key 並標示 known=false，不將未知選項偷偷歸類。成員／附件／部門可先 parseArray，再依部署契約驗元素型別。關聯 count 只辨識筆數型別，是否為多條關聯仍須核對欄位 metadata。

正式資料不要 console.log 原始值、完整列或選項內容；只記去敏事件類型。捕獲解析錯誤後顯示資料格式錯誤，驗收應判失敗，不能以空值／0 掩蓋。日期時區與金額精度另依業務契約處理，本工具不提供金額任意精度計算。
