# niio 本機 MCP

這是 niio-skills 隨附的 stdio 服務，隨每位使用者自己的 Agent 啟動，不開放監聽埠，不依賴 niio-dev01 的試驗容器。它仍透過原平台 `https://niiodemo.apsm.com.tw/mcp` 並以使用者本人認證操作，不是平台後端替代品。

完整安裝／更新／回復入口：`python scripts/install_bundle.py setup|update|auth|verify`，從套件根目錄執行；不要單獨複製此資料夾後手動改未知設定。詳見 `docs/LOCAL_MCP_INSTALL.md`。

Node 24 LTS+；相依套件固定於 package-lock.json，離線 ZIP 包含相依套件與其授權。從來源建置：

```sh
npm ci --ignore-scripts --no-audit --no-fund --bin-links=false
node --test test/*.test.mjs
```

只允許原公開 MCP 目的地；沒有將個人 PAT 寫進套件，沒有攜帶原廠後端 JAR／DLL、測試伺服器私鑰或 NAS 設定。Windows 新認證使用 CurrentUser DPAPI；舊認證來源需明確選擇，未知 helper 不執行。所有寫入仍遵循原平台權限，不因新版失敗而自動向舊端點重送。

修正與限制見完整安裝文件；篩選器與知識庫未修復項目不能因安裝本機 MCP 就列為通過。
