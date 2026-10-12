# niio 網站技能

使用 niio 作為網站內容管理後台。從 SKILL.md 開始，依 references/niio-as-database-guide.md 設定部署。

網站模板採「瀏覽器 → 同源網站後端 → niio REST」架構。秘密只存後端；公開內容由後端限制資料集、發布條件與輸出欄位。

assets 內的 config.js、api.js、main.js 模板供前端使用；server.mjs 與 server.config.mjs 模板必須放在靜態發布目錄以外。預設沒有啟用資料集，必須先確認部署與完成唯讀驗證。

隨附模板僅支援公開內容唯讀列表。會員、內部資料、詳情及寫入功能需另加身分與權限設計。舊版前端直連模板應整組遷移。
