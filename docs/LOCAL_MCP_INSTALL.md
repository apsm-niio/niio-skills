# 八個技能與本機 MCP：安裝、更新與回復

本版以每位使用者自己的電腦執行 `niio_local_mcp`。不需要 NAS、Docker、內網測試埠或 niio-dev01 的新容器；仍透過原 `https://niiodemo.apsm.com.tw/mcp` 操作平台，並使用每人自己的認證。其他 niio 部署尚未納入本版驗收，不要把認證送往自行猜測的網址。

## 一般使用者：首次安裝

需要 Python 3.10+ 與 Node.js 24 LTS+，一般使用者權限即可。取得維護者提供、已核對 SHA-256 的完整離線 ZIP 並解壓；ZIP 已包含固定版本的 JavaScript 相依套件，不需要 npm 連網安裝。從 GitHub 原始碼取得時，安裝器只在隔離版本目錄執行固定 lockfile 的 npm ci，停用安裝腳本；網路失敗不改已安裝技能與 MCP 設定。完整離線 ZIP 可從通過的 GitHub Actions「本機 MCP 安裝與回復」紀錄取得；GitHub 的 Download ZIP 只是原始碼，並未內含 node_modules。

先停止使用這八個技能的 Agent 工作階段，開啟 PowerShell，進入解壓後的 `niio-skills` 資料夾：

```powershell
python .\scripts\install_bundle.py setup
if ($LASTEXITCODE) { throw '安裝未完成，請保留輸出與收據' }
```

預設安裝到目前使用者的 `.codex`。若 Node 不在 PATH，加上 `--node 'C:\你安裝的位置\node.exe'`；測試或其他 Codex 根目錄使用 `--codex-home 'C:\你選定的目錄'`，不要把測試根目錄當成實際 Codex 已載入的證據。

安裝器在修改技能／設定之前，會從最後的版本目錄實際載入服務，確認 Node 可以啟動。本輪對照重現 Windows Node 22.12 在特定中文目錄載入 SDK 時原生崩潰，同一 SDK 使用 Node 24.19 可正常載入；遇到 `RUNTIME_LOAD_FAILED` 請使用較短的 Codex 根目錄或相容 Node 版本，不會把無法啟動的服務切進現有設定。中文及空白路徑另有實機驗收，不把兩者混同為必然不支援。

成功輸出含 `receipt` 絕對路徑，請保存。這一步安裝八個技能、獨立本機服務及 `mcp_servers.niio_local_mcp`，**不代表認證或工具已載入成功**。

接著在互動終端執行：

```powershell
python .\scripts\install_bundle.py auth
if ($LASTEXITCODE) { throw '授權未通過；原認證未被覆蓋' }
python .\scripts\install_bundle.py verify
if ($LASTEXITCODE) { throw '唯讀驗收未通過' }
```

`auth` 以隱藏輸入接收你自己的 PAT，請不要貼在聊天、命令列、截圖或報告中。Windows 使用目前帳戶的 DPAPI 加密儲存；先以暫存密文完成唯讀連線驗證，成功才取代原認證，失敗保留舊值。應用 AppKey／Sign 不能拿來填這個 PAT 提示。授權來源使用自己已確認的個人令牌介面，不借用他人令牌，不擴成管理員來通過驗收。

認證密文位於 `.codex/niio-local-mcp/auth.json`，不能跨 Windows 使用者／電腦直接搬用。解密時經子程序的 stdout 私有管線傳遞給本機 MCP 程式，不能宣稱完全不經 stdout；請勿自行執行或錄製內部認證程式。安裝包不含令牌、個人設定或伺服器私鑰。

非 Windows 的程式環境可使用 `NIIO_LOCAL_TOKEN` 環境變數；本版安全持久儲存及實機使用者驗收以 Windows 為範圍。不要把環境變數的值直接寫進 TOML 或分享安裝包。

最後重新開啟 Codex／工作階段，確認八個技能可讀以及 `niio_local_mcp` 工具實際出現。安裝器與獨立 SDK 驗收不代表每個既有對話已熱載入。不要為了重新載入而刪除其他 MCP。

## 已有技能或手動 MCP 的使用者

安裝器預設拒絕覆蓋無法辨識的既有技能或手動 `niio_local_mcp`。先選定與目前八個技能逐檔相符的已審閱來源，作為 `--baseline`。如有自訂檔案，先保存差異，不要強制覆蓋。

已明確停用的本機 MCP 在接管及更新時仍維持停用，verify 會拒絕啟動；恢復使用需由使用者明確決定。

明確接管手動本機 MCP 設定時才使用 `--adopt-existing-local`；原區塊會備份，回復時可還原。若希望沿用自己原本 `niio_personal_mcp` 的認證，可明確加 `--reuse-existing-auth`；必要時用 `--legacy-config` 指向該設定檔。只支援已審閱的既有認證來源與指定 helper，不會執行任意命令或改其他人的設定。

```powershell
python .\scripts\install_bundle.py setup --baseline 'C:\已核對的舊來源' --adopt-existing-local --reuse-existing-auth
```

這些旗標不是一般新使用者必填項目。未知 helper 或錯誤部署會停止；改用本版 `auth` 安全提供自己的 PAT，不把 MCP 憑證移作 REST 或 CLI 登入。

## 更新

取得並核對新版 ZIP，解壓到新資料夾，停止相關 Agent 工作階段，從新版資料夾執行：

```powershell
python .\scripts\install_bundle.py update
if ($LASTEXITCODE) { throw '更新受阻；請勿重新覆蓋自訂內容' }
python .\scripts\install_bundle.py verify
```

更新自動以受管理的舊版作為八個技能的 baseline，保留認證、其他 MCP、模型設定及工具審批政策。新版存放於不可混用的版本目錄，最後才切換 MCP 啟動設定。已有自訂技能、服務檔或本機 MCP 區塊時會停止；其他無關設定的變更會保留。相同版本重跑會核對後回傳既有收據，不疊加重複安裝。

## 回復／解除本次安裝

使用目前或較新套件中的工具，帶入該次 `setup`／`update` 回傳的收據：

```powershell
python .\scripts\install_bundle.py restore --receipt 'C:\該次輸出的完整收據路徑\receipt.json'
if ($LASTEXITCODE) { throw '回復受阻；保留收據、備份與版本目錄' }
```

更新收據會回復上一版技能與 MCP；首次安裝收據會撤銷本次新增項目，保留其他技能／MCP。需依相反順序回復較新的安裝，不能跳過新版直接還原舊收據。無其他設定變更時會精確還原原設定；若新增了無關設定，僅回復自己的 MCP 區塊。

回復會記錄進度，正常例外會嘗試自動回復；中斷後可對同一收據續跑。已完成項目會重新核對，不覆蓋自訂內容。失敗時保留備份與完整收據路徑，不刪鎖、不修改收據假造成功；斷電／強制終止留下的鎖需先人工確認沒有活躍程序。不是跨技能、設定與狀態檔的單一檔案系統原子交易，也不承諾斷電耐久性。

備份、舊版本及加密認證會保留，不因回復刪除個人 PAT。安裝器不改系統 PATH、全域 Node、原 MCP 或 NAS 設定。更新／回復後重新開啟工作階段。

## 驗收與已知限制

`verify` 啟動實際 stdio MCP、取得工具目錄，僅呼叫 `get_current_user`，不建立資料或觸發流程。看到 `passed: true` 才表示該帳號當下唯讀認證成功；不能延伸成所有工具、角色或 OAuth 都已驗收。

本機修正涵蓋指定欄位清單讀回、數字寫入驗證、單／多選工作流正規化及內部起始別名。篩選器名稱遺失仍是上游缺陷，依指示暫緩；知識功能仍受後端部署與額度限制。CLI 與 REST 需要分開驗證；這次安裝不會替 CLI 登入。

目前測試範圍與收據見 [本機套件驗收](LOCAL_MCP_ACCEPTANCE.md)。官方設定依據：https://learn.chatgpt.com/docs/extend/mcp?surface=cli 。
