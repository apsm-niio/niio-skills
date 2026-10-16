# 整套 niio-skills 交付狀態

日期 2026-10-16。來源基準 `0fa9c94cb6557ffff63d2f13e80873c34b037ac7`，固定上游 `71e0488b48ac06156249b62741fb16f0be4a1496`。八個頂層技能、builder 內含 plan/build，共十份 SKILL.md。程式／文件完成不等於部署驗收通過；本輪沒有 niio MCP／REST 呼叫、觸發、角色或資料修改。

|技能|程式／文件完成|離線驗證|部署實測證據|外部受阻|
|---|---|---|---|---|
|niio-mcp-app-builder（含 plan/build）|生成來源同步；掃描須明確根目錄、更新查詢改為選用；錯誤中繼資料受控失敗、原輸出保留；安裝／回復文件|生成、隔離安裝、checkpoint、欄位 refresh／填值、唯讀掃描回歸；5 項 Windows 連結案例受阻|沿用既有應用／資料讀回與按鈕入口成功證據；不把 MCP trigger 錯誤算成功；未重建|G6 歷史入口／下游／實例日誌，G7 Windows 連結；角色／同仁暫緩|
|niio-apiv3-data|修正 filter 群組範例、型別與工作流完成敘述；移除浮動依賴安裝；保留部署契約限制|生成／安裝與 mock 捕獲正反例|無本部署 REST 成功證據；舊 404 HTML 只作歷史線索|G1、G2|
|niio-api-website|現有同源後端白名單模板沿用；公開資料、設定與驗收文件完整|既有 5 項安全測試在整合輪通過；未改模板|沒有網站部署或本部署 REST 實測|G1、G2、G4|
|niio-view-plugin|重整初始化／設定／發布指引與重複矛盾；跨平台預檢、實際 ID、明確 host/webui；純函式解析與 SDK 驗收材料|本機 mdye help 隔離驗證；預檢、參數、型別解析與 mock SDK；無模板下載／push|無平台 SDK／瀏覽器／推送成功證據|G2、G5；0.0.38 不等於部署相容認證|
|niio-cli|保留 hap 技術入口，與 mdye 分離；安裝、設定、使用與限制統一文件|生成／隔離安裝／mock 捕獲契約|沒有 hap 本機或部署成功|G3、G2|
|niio-cli-environments|既有環境選擇與單次 profile 文件核對；未改登入|生成／隔離安裝；無真實 profile 測試|無|G3|
|niio-cli-data-query|修正必填／預設矛盾與 Bash 續行；實際旗標以版本 help 為準|生成／隔離安裝／mock 捕獲契約|無；MCP 資料總額不是 CLI 驗收|G2、G3|
|niio-cli-app-editor|自動升級敘述依版本限定；發布需授權且獨立驗收；schema 為參考契約|生成／安裝／10 份 JSON Schema 編譯與 edit-spec 正反例；未冒稱伺服器 schema 全相容|無；未改應用結構|G2、G3|

## 修正與驗證界線

所有主技能與其腳本／模板均逐份閱讀；額外追讀重複的外掛開發／欄位參考，移除自動全域安裝、推測初始化目錄、固定除錯埠、關閉防火牆、無條件發布等互相矛盾的指令。保留合法技術名稱，品牌顯示使用 niio。override manifest 對上游來源 SHA256 做變更守門，新 helper 亦綁定已審閱來源；重新生成逐位元組核對，避免下次本地化覆蓋。

Windows 生成器預設 cp950 解碼缺陷已改成明確 UTF-8。測試依賴從前輪固定版本 venv 複製至本輪隔離 venv（同 Python 3.10.6），沒有網路安裝或全域修改。測試子程序使用工作區隔離 TEMP；預設沙箱 TEMP 的 rename 拒絕另記限制。舊 hardlink/symlink 5 案不改測試、不 skip、不放寬原子寫入。

一輪整合包含固定來源生成、品牌／授權／十份 frontmatter、八項隔離複製、Python 回歸、網站及外掛 Node 測試、四通道 mock；之後修改僅重測受影響項目。詳細數字與 CI 由本次交付測試報告記錄，不能只用綠色 CI 宣稱 Windows 或部署全部通過。

沿用證據：前批 niio-batch-completion-report、niio-trigger-audit／完整驗收證據、2026-10-16 Windows 診斷與能力矩陣。含真實 ID 的受控資料留在原交付資料夾，不上傳公開 PR。需要維護者的最少資料及人工驗收清單見 [ACCEPTANCE.md](ACCEPTANCE.md)；操作指令見 [INSTALL.md](INSTALL.md)；可執行離線包見 [acceptance](../acceptance/README.md)。

正式技能仍為原版本；本工作階段目錄證據只列出 builder／plan／build，其他七技能未註冊。檔案核對與此工作階段實際載入證據分開記錄；不能證明啟動時已完整載入所有內容。
