# CLI 相容性核對（2026-10-16）

|項目|本機 mdye-cli 0.0.38|技能所需 hap-cli|
|---|---|---|
|用途|檢視外掛模板、開發伺服器、打包與推送|組織、應用結構、資料查詢、流程等管理|
|入口|package.json 的 bin：mdye → cli.js；版本輸出 beta-0.0.38|hap；目前 PATH／現用 Python 未找到，不代表其他機器未安裝|
|實際 help|auth、init、start、build、push、whoami、logout、sync-params|本機無工具，不能將技能中 0.9.0 字典說成當前已驗證命令|
|初始化|init view；--id、--template、--host、--webui|依實際版本 guide/help 核對；不能改寫成 mdye|
|設定|專案 mdye.json：id/template/host/webui/version；全域 .mdye-config 為工具認證|既有 profile、組織／應用選擇；格式需實際版本確認|
|認證|auth 開啟瀏覽器；不是腳本輸入帳密|官方文件有 auth login、accounts、whoami 與 --profile；本部署未驗證|
|網路注意|參數解析前載入 cwd/home 設定；沒有 host 時有上游預設；init 下載模板，push 上傳|可能自動更新，須依版本確認；help 不等於離線保證|

本次在空 home/cwd，以 Node preload 攔截 HTTP(S)、net/fetch，執行 --version 及 init/start/build/push --help；只輸出說明，未執行命令本體。正式 .mdye-config 未讀取或修改。套件來源亦核對 cli.js、core.js、init.js、start.js、auth.js。Node 22.12.0 可執行本機 help，不代表模板建置與部署 SDK 已相容。

官方來源：[檢視開發指南](https://help.mingdao.com/extensions/developer/view/)、[內網指引](https://help.mingdao.com/plugin/mdye-intranet-guide/)、[CLI 指南](https://help.mingdao.com/zh-Hant/ai/cli/)。前者要求從平台複製初始化命令；內網文件要求 Node >20，文件中的 beta 版本範例不是 0.0.38 的部署認證；CLI 組織存取是否開放須維護者確認，本輪沒有啟用。

現有參考文件的參數與 API 契約僅作範例，部署版本不一致時停止；不可用名稱替換當作相容層。不得複製 MCP token 作 REST／CLI 認證，也不把忽略憑證檢查作為排錯方法。
