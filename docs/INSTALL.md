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

保存 receipt 絕對路徑；備份在 skillRoot 的父目錄 `.niio-backup-*`，不混入技能掃描目錄。新版本安裝後如有自訂變更或舊備份被修改，回復會拒絕覆蓋；先另存差異、由維護者核對。工具不刪除任何備份。複製在隔離 staging 完成後核對 SHA256，日誌原子寫入，逐技能 rename；整套切換不是跨八個目錄的單一原子交易，執行期間必須停止 Agent。一般可捕捉的安裝例外自動回復；強制終止／斷電可能留下鎖與部分切換，保留 receipt、鎖、全部目錄，先人工確認沒有存活程序，勿盲刪鎖。沒有斷電耐久性保證。

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
