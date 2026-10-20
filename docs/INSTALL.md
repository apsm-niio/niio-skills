# 整套安裝、更新與回復

支援範圍：八個頂層技能（builder 內含 plan/build），Python 3.10+；網站／外掛離線測試使用 Node 22。技能複製不安裝 CLI、SDK、不登入、不寫 MCP 設定。正式環境採用前須自行選定已審閱的完整 commit。

先將儲存庫以 `core.autocrlf=false` 取得至獨立目錄，checkout 指定完整 40 位 commit，確認 `git rev-parse HEAD` 符合且 `git status --porcelain` 為空；記錄 SHA。來源取得失敗就停止，勿改用浮動 main。舊版 baseline 也須相同方式取得；本次正式 builder 的已知基準是 `0fa9c94cb6557ffff63d2f13e80873c34b037ac7`。工具驗證檔案一致性，來源真偽／commit 選定仍由這個步驟負責。

在所有使用技能的工作階段停止後，PowerShell 執行一次更新（把路徑改為已核對的絕對路徑）：

```powershell
$receipt = python "$newCheckout/scripts/install_bundle.py" install --source $newCheckout --baseline $oldCheckout --target $skillRoot
if ($LASTEXITCODE) { throw '安裝受阻；保留錯誤與備份，勿重複覆蓋' }
$receipt | Set-Content -Encoding utf8 ./niio-install-receipt-path.txt
```

初次安裝省略 `--baseline`；只安裝了舊 builder 也可使用 baseline，其他七項會新增。`$skillRoot` 是明確選定的 Agent 技能目錄，例如 Codex 的 `.codex/skills`，不是應用專案。不要讓兩個安裝程序同時執行。

一次回復：

```powershell
python "$newCheckout/scripts/install_bundle.py" restore --receipt $receipt
if ($LASTEXITCODE) { throw '回復受阻：保留備份，人工檢查差異' }
```

保存 receipt 絕對路徑；備份在 skillRoot 的父目錄 `.niio-backup-*`，不混入技能掃描目錄。工具不刪除任何備份。複製在隔離 staging 完成後核對 SHA256，日誌原子寫入，逐技能 rename；整套切換不是跨八個目錄的單一原子交易，執行期間必須停止 Agent。

### 回復中斷與續跑

receipt 的整體狀態為 `restoring` 時，各項 `restoreState` 會記錄 `pending`（尚未搬移）、`saving-new`（準備移出新版）、`new-saved`（新版已移出／待搬回舊版）、`restoring-old`（準備搬回舊版）、`restored`（此項完成）。每次搬移前後原子保存進度；重新執行同一個 `restore --receipt` 即可續跑，完成項不再搬移。

進度可能因搬移成功後寫入失敗而落後，因此續跑還會核對目標、舊備份、`.new` 暫存及 `.restored-new` 保留副本的配置與 SHA256。舊版 receipt 沒有逐項進度時，只要這些證據完整，也可辨識已回復項目；不會只因目標內容等於舊版就猜測成功。新舊版內容完全相同的情況也依目錄配置區分。

回復前先檢查全部項目，之後每項執行前再核對；尚未回復的新版、已恢復舊版、備份或保留副本出現自訂變更、缺檔或衝突時，停止而不覆蓋。先另存差異並由維護者核對，不修改 receipt 欺騙檢查。重複回復已完成 receipt 仍會驗證現況，正常時不做搬移。

一般安裝例外會嘗試自動回復；如果自動回復也失敗，錯誤會保留原安裝錯誤、回復錯誤及 receipt 絕對路徑。排除造成 rename／寫入失敗的原因後，使用新版工具對該 receipt 執行上述回復指令，勿重新安裝來覆蓋混合狀態。失敗的 receipt 原子替換不會留下阻擋續跑的固定暫存檔，舊 receipt 保持可讀。

可捕捉例外結束時釋放本次鎖；強制終止／斷電可能留下鎖與部分切換，保留 receipt、鎖、全部目錄，先人工確認沒有存活程序再由維護者處理殘留鎖，勿盲刪鎖。沒有斷電耐久性保證，也不自動接管其他程序的鎖。

重開工作階段，逐項確認八個技能名稱出現，並明確載入所需 SKILL.md。檔案安裝成功、工作階段載入、遠端能力是三種證據；不能互相替代。

## 設定與範例

- builder：從明確專案根目錄唯讀掃描 `python <builder>/plan/scripts/scan_apps.py <projectRoot>`。預設不檢查網路更新；`--check-updates` 是明確選用。建置／續跑需另有使用者授權，不能用驗收安裝當作建置授權。
- API：先提供完整唯讀 URL、方法、適用的認證模式與回應契約，再走 acceptance/README.md；沒有資料時僅 mock。
- 四個 CLI：先核對獨立的 hap 工具與 profile，再依該版本 help；mdye 無法替代。
- 網站：採同源後端模板；server.config 的資料集預設停用。只在 REST 已確認且公開欄位核准後配置；秘密留在後端環境變數。
- 外掛：從平台取真實初始化參數，以 view_project.py init-plan 產生 argv；preflight 只檢查明確專案路徑。工具不代替實際模板安裝或部署驗收。

## Windows 適用限制

現環境 hardlink 回 WinError 5，symlink 建立回 1314。四項舊名稱檔案遷移測試及一項 symlink 測試受阻；不表示所有 Windows 機器都不支援。舊名稱遷移要求不覆蓋的 hardlink，保留原子性與原檔保護，不能改成一般覆寫來過測。全新 niio 名稱專案、唯讀掃描、一般原子替換不因此受阻。可由維護者在已允許連結的受控環境遷移副本，逐檔核對後再採用；本輪不提權、不改 ACL。

此次 Windows 沙箱預設 TEMP 的原子 rename 亦遭拒；同一測試使用工作區內隔離 TEMP 通過。必要時只對測試子程序指定 TMP/TEMP 至自己可寫的隔離目錄，不修改系統環境或關閉防護。若仍拒絕，保留錯誤與原檔，換已核准環境驗證，不降低檔案保護。

## 新使用者：技能安裝後另做 MCP 授權

安裝八個技能只提供操作指引與本機工具；MCP URL 設定完成不等於登入成功，也不代表伺服器支援 OAuth。依序完成：固定版本安裝 → 工作階段技能可讀 → 個人 MCP 授權 → 唯讀驗收。

### 兩種授權不要混用

|用途|取得位置|提供方式|
|---|---|---|
|個人 MCP Bearer PAT|在目標 niio 網站登入自己的帳號，從頭像／帳號設定進入「授權與存取」或「個人存取權杖」；依該部署介面新增並限制範圍及期限|由使用者在本機隱藏輸入，透過已確認支援的客戶端機制提供 Authorization；不要貼入對話、命令列、PR 或報告|
|應用 AppKey／Sign|該應用的「API 說明 → 應用授權 → 授權管理」；API V3 分頁是介面文件，不是密鑰產生頁|保存在受控本機檔案／秘密儲存；只提供來源路徑或變數名稱。REST 方法、入口與標頭以該部署契約為準|

若看不到個人存取權杖入口，由組織管理者確認部署功能及帳號政策；不要借用別人的 PAT、改用應用密鑰或猜測 OAuth。授權只選本次需要的應用與讀取能力；不要為了驗收擴成管理員。

### 本機提供與重新載入

1. 先確認目標 MCP 網址與目前 Codex 版本；備份設定，保留其他 MCP 項目。由使用者本機提供自己的 PAT，不由 AI 在對話索取內容。
2. 本次同仁使用 Codex `0.163.0-alpha.10.2`，透過 `http_headers_helper` 成功連線。設定腳本以隱藏提示接收 PAT，Windows DPAPI 保存密文；helper 在客戶端呼叫時，經程序 stdout 傳送 Authorization JSON 給 Codex。stdout 是程式介面，不能宣稱 PAT 完全不經 stdout；不得手動執行 helper、錄製其輸出或寫入明文日誌。
3. **這是指定版本的驗收證據，不是所有 Codex 版本的支援保證。** 其他版本應先查該版本的設定支援；未支援時停止該方式，不塞入未知設定。兩份同仁腳本未納入此儲存庫、未經本次來源審查，不能從本文件直接取得可執行的 helper。
4. 完成本機設定後關閉並重新開啟 Codex 工作階段，確認八個技能名稱及所需 SKILL.md 可讀，且 niio MCP 工具出現。只有設定可解析、enabled 或 Auth Unknown，均不足以判定連線成功。
5. 執行 [新使用者唯讀驗收](ACCEPTANCE.md#新使用者唯讀驗收)。實際唯讀請求成功才完成此段驗收，不順便建立資料或觸發流程。

### Windows PowerShell 5.1 腳本編碼

新使用者案例中，含中文的 UTF-8 無 BOM 腳本被 Windows PowerShell `5.1.26100.9444` 以系統 ANSI 解讀，造成 ParserError。`Set-NiioMcpPat.ps1` 與 `niio-mcp-headers.ps1` 轉為 UTF-8 with BOM、CRLF 後，以同一 powershell.exe 的 Parser API 檢查通過，後續 MCP 連線成功。這個修正與 hardlink／symlink 權限限制是不同問題。

交付給 Windows PowerShell 5.1 的含非 ASCII 腳本應保存為 UTF-8 with BOM，再用實際執行的 powershell.exe 做純解析檢查。不要只用 PowerShell 7 或另一個 shell 的解析結果代替；BOM 檢查也不代表腳本語法或行為已驗證。修正編碼不需要提升管理員權限或放寬系統執行原則。

本儲存庫目前沒有 `.ps1`／`.psm1`／`.psd1` 交付檔；Markdown 中的 PowerShell 範例若另存腳本，也適用上述編碼要求。兩份同仁腳本的來源缺口與後續負責者見 [整合進度](ONBOARDING_PROGRESS.md)。
