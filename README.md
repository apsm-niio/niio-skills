# niio Skills

適用於 niio 的台灣繁體中文 AI Agent 技能集合，涵蓋應用建置、資料查詢、API 串接及擴充開發。

## 整套對外交付

本專案交付的是 **niio 品牌、繁體中文、環境設定指引與必要相容處理的 Skills 移植版本**。現有證據支持品牌移植與指定環境的唯讀試用，不代表每個遠端功能、正式部署或上游全部行為均已驗收；網站模板已有公開唯讀的功能範圍差異。

完整八個技能的 [交付結論、差異及 A／B／C 分工](docs/DELIVERY.md)、[安裝／更新／回復](docs/INSTALL.md)、[CLI 相容性](docs/CLI_COMPATIBILITY.md)、[可執行驗收包](acceptance/README.md)、[維護者需求與人工驗收](docs/ACCEPTANCE.md)。下方舊安裝例只適用 builder；整套交付請使用 install_bundle.py。部署端未完成事項不自動成為品牌移植的交付阻擋項，也不歸責於使用者不熟悉後端工具。

## 安裝與啟用（固定版本）

先選擇已審閱的完整 40 位 commit，不使用浮動 `main` 當安裝版本。MCP builder 的本機腳本需要 Python 3.10 以上；Git 用於取得與核對來源。一般使用不需要本儲存庫的轉換依賴或 Node.js。只有需要 CLI 的功能才另需部署支援的 CLI 與既有登入 profile；不自動安裝或登入。

以 Codex 為例，技能預設放在 `$CODEX_HOME/skills`，未設定時為使用者家目錄的 `.codex/skills`。其他 Agent 請依其技能設定選擇目錄，不把技能放進應用專案當作替代。以下 PowerShell 範例只安裝 MCP builder，不補裝 API／CLI：

```powershell
$commit = '<填入已確認的完整 40 位 commit>'
if ($commit -notmatch '^[0-9a-f]{40}$') { throw '需要固定 commit' }
$checkout = Join-Path ([IO.Path]::GetTempPath()) ('niio-skills-' + [guid]::NewGuid())
git -c core.autocrlf=false clone --no-checkout https://github.com/apsm-niio/niio-skills.git $checkout
if ($LASTEXITCODE) { throw '下載失敗' }
git -c core.autocrlf=false -C $checkout checkout --detach $commit
if ($LASTEXITCODE -or (git -C $checkout rev-parse HEAD) -ne $commit) { throw '版本不符' }
$skillRoot = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'skills' } else { Join-Path $env:USERPROFILE '.codex/skills' }
$dest = Join-Path $skillRoot 'niio-mcp-app-builder'
$source = Join-Path $checkout 'skills/mcp/niio-mcp-app-builder'
if (Test-Path -LiteralPath $dest) { throw '已安裝：先按下方更新流程備份及比對，勿覆蓋' }
New-Item -ItemType Directory -Force -Path $skillRoot | Out-Null
Copy-Item -LiteralPath $source -Destination $dest -Recurse
python (Join-Path $checkout 'scripts/verify_install.py') $source $dest
if ($LASTEXITCODE) { throw '逐檔驗證失敗，保留副本供檢查' }
```

更新既有安裝時，先停止使用該技能的工作階段，記錄舊 commit，將完整舊目錄備份到技能目錄外；用舊版本的乾淨副本與舊安裝執行 `verify_install.py`。它忽略 Python 快取，會列出新增、缺少、內容不同的檔案；有自訂差異就保留並人工合併，不直接覆蓋。確認無自訂變更後，將舊安裝移至另一個保留目錄，再複製已驗證新版到原位置並逐檔核對。失敗時保留新版診斷副本，將備份複製回原位置；不要刪除專案或 MCP 設定。Unix 複製請使用 `cp -a` 保留腳本權限。

重新開啟 Codex 工作階段，確認技能清單有 `niio-mcp-app-builder`，以名稱明確指定使用。`/niio-builder` 是技能描述的提示名稱，不保證每個客戶端都註冊斜線命令。檔案一致、工作階段載入、MCP 連線是三項不同驗證，不互相替代。

## MCP 設定與排錯

由部署管理者提供已確認的 MCP 端點、驗證方式與組織存取權，再於客戶端設定連線。本技能不寫入 MCP 設定，不收集或印出 Token。網站、MCP 與 REST 路徑可能不同，不由圖示或 MCP 網址猜測其他路徑，也不將 MCP 憑證用於 REST。範例網域不代表其他部署已驗證。

|情況|確認方式|
|---|---|
|技能未出現|確認安裝位置、`SKILL.md` 與檔案比對結果，重新開啟工作階段|
|找不到 MCP 工具|確認客戶端已載入連線；以目前工具清單及 schema 為準|
|多個 MCP 服務|先確定部署；不要跨服務混用 ID 或憑證|
|401／403 或組織不可見|由管理者核對帳號、組織與授權；不自動改角色或放寬權限|
|404 HTML／回應型別不符|保存去敏錯誤、工具與參數、時間及可用 request ID；停止寫入，不以其他入口盲重試|
|檢視或資料不可見|分別唯讀核對表、檢視、應用歸屬與有效權限，不直接重建資料|

首次連線只在使用者允許後呼叫 `get_org_list` 等唯讀工具。新安裝不能用沿用登入的成功結果宣稱初次登入通過。

## 維護與離線驗證

轉換與測試使用 Python 3.10 以上（CI：3.12）及 Node.js 22 以上。在獨立虛擬環境安裝 `requirements-validation.txt`，從 `localization/upstream-state.json` 取得固定上游 commit，將其快照放在獨立目錄後執行：

```text
python scripts/validate_release.py --upstream-source <上游快照絕對路徑>
python -m unittest discover -s tests -p "test_*.py" -v
node --test tests/test_website_gateway.mjs
```

第一項在暫存目錄重新生成、檢查品牌與技能格式、逐檔比對生成產物、比對授權、隔離安裝核對；不覆蓋安裝目錄，不連線 niio。測試的更新通知使用模擬 API，不建立真實 Issue，也不執行上游同步。遠端部署、角色帳號、瀏覽器畫面與後端執行紀錄需另行授權及驗證。

## 更新通知與確認

每月 1 日台灣時間上午 9 點檢查上游版本（GitHub 排程可能延遲）。有新版本時建立 GitHub Issue，通知 @sigurd0414，附上提交紀錄、異動檔案及完整比較連結。沒有新版本不通知，同一版本不重複通知；Email 是否寄送依個人 GitHub 通知設定。

檢查流程不修改技能、不啟動同步。閱讀更新內容並決定採用後，開啟 [確認後同步並產生繁中技能](https://github.com/apsm-niio/niio-skills/actions/workflows/sync-upstream.yml)，按 **Run workflow**，選擇 `main`，在 `upstream_commit` 填入通知中的完整 40 位版本 SHA，再執行。同步只使用指定且存在於上游 main 歷史中的版本，並套用台灣用語、niio 設定及既有驗證。

不想更新時不執行即可；關閉通知 Issue 不會觸發同步。每日自動同步與推送後自動同步均已取消；調整本地轉換規則後，也需手動指定版本執行同步。

需要提前檢查時，可手動執行 [每月檢查上游更新（僅通知）](https://github.com/apsm-niio/niio-skills/actions/workflows/check-upstream.yml)。修改檢查流程本身時也會執行一次檢查。

第三方元件依各自授權條款使用，相關版權與授權聲明將隨附保留。
