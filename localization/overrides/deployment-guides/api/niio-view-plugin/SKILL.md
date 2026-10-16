---
name: niio-view-plugin
description: 建立和開發niio 自訂檢視外掛的技能。立即觸發條件：使用者提到"niio 檢視外掛"、"自訂檢視"、"mdye"、"檢視開發"、"外掛開發"、"初始化檢視專案"、"啟動檢視除錯"。提供完整的開發工作流程、API 使用指南和最佳實踐。
license: MIT
---
> **部署設定**：範例 API 使用 `https://niiodemo.apsm.com.tw`；其他部署須替換為該環境網址與憑證。API、MCP 與網站網址必須使用本次選定部署環境的已確認設定，三者可能不同，不得只依 MCP 網址推測 API 或網站位置。範例網域不代表 REST 路由已驗證；MCP 成功也不代表 REST 或 CLI 相容。使用 REST 功能前，須依部署文件確認路徑與驗證方式，先完成唯讀測試；404 HTML 時停止，不重試寫入。下方 `.example.invalid` 網址只是不可連線的佔位範例，執行前必須替換；未確認網址時先詢問，不得向佔位網址傳送憑證。圖片與附件只能使用使用者提供或已授權的素材網址。

> **對外表達規範**：對使用者的說明、提示與成果摘要，統一使用 niio 品牌及台灣繁體中文。執行所需的技術名稱、套件、命令、API 參數與路徑請保留；只在操作或除錯所需的程式碼中呈現，勿將它們用作產品標題或品牌名稱。


# niio 自訂檢視外掛

此技能使用 `mdye-cli` 開發檢視；資料與應用管理技能使用另一套 `hap-cli`。兩者命令、登入及設定不可互換。

## 已確認範圍

本機核對 `mdye-cli 0.0.38` 的套件來源；離線測試使用 Node.js 22.12.0。部署端初始化、登入、SDK、建置及推送尚未實測，不代表支援所有 niio 部署。
官方內網指引（來源見交付文件 docs/CLI_COMPATIBILITY.md） 要求 Node.js 高於 20；實際採用版本還須符合專案鎖檔。
版本顯示 `beta-0.0.38` 是套件自己的格式。`mdye --help` 不會證明部署相容性。

## 初始化

先取得部署開發面板提供的完整 `mdye init view` 命令，保留真正的 worksheetId-viewId、template、host、webui。不得自行組合時間戳 ID、由 MCP 推測 host，或略過 host 而連到工具預設環境。

不自動安裝全域工具或切換 npm registry。在獨立工具目錄安裝經審核的固定版本（例如本次來源核對的 `mdye-cli@0.0.38`）後，明確使用該工具的執行檔；此步會下載套件，應由使用者選定的網路與套件來源執行。不要以無版本 `npx` 隱式下載。

跨平台參數檢查，只產生命令陣列，沒有網路或登入副作用：

```powershell
python scripts/view_project.py init-plan --id "$worksheetId-$viewId" --template React --host $confirmedHost --webui $confirmedWebui
```

上述變數必須來自開發面板。確認輸出的 argv 後才在空白工作目錄執行；實際產生的資料夾以工具輸出及其中的 mdye.json 為準，不猜固定資料夾名。0.0.38 的預設名取 ID 第二段，遇重名可能互動改名。生成後核對 mdye.json 的 id、template、host、webui、version；不得把 MCP token 填入其中。

認證由 `mdye auth` 的瀏覽器流程完成；全域 `.mdye-config` 保存工具認證，專案 `mdye.json` 不等於此認證檔。未獲授權不讀取、匯出或更動認證。工具在解析命令前會讀取這兩種設定，因此隔離測試必須隔離 home 與 cwd。

## 已有專案

先審查 package.json 及鎖檔；有相符 package-lock.json 時在專案內執行 `npm ci`，無鎖檔時先解決版本鎖定，不清空快取或改全域 registry。

```powershell
python scripts/view_project.py preflight "C:/path/to/explicit-project"
```

成功只代表本機必要檔案存在且設定格式通過。確認授權後，在輸出 cwd 執行 argv（`mdye start`）。使用實際終端印出的 URL；埠不保證為 3000。SDK 驗收需要瀏覽器開發面板及部署支援，不用等待秒數推定成功。

## SDK 使用與驗收

`mdye` SDK 與 `mdye-cli` 套件不同。由已確認模板安裝 SDK；在平台檢視中取得 `api`、`config`、`env`。先驗證 worksheetId/viewId 與目標相符，再以 pageSize=1 的 getFilterRows 唯讀查詢核對回應。沒有部署權限時僅用 mock，不將 mock 通過記為部署通過。

相關範例見 `references/niio-view-plugin-dev-guide.md` 與 `V3_API_INTEGRATION.md`；屬參考契約，部署支援仍待驗收。解析時檢查物件／陣列型別；缺值、解析錯誤與數字 0 分開。不要記錄完整列資料或 token。關聯資料避免無界 Promise.all，使用分頁與有界批次。

## 建置與發布

先核對 `mdye build --help`、模板的 package scripts 與本機建置輸出，再於已授權情況使用 `mdye push`。push 成功不等於全組織可見：還需要平台發布狀態、可見範圍、版本及實際開啟檢視證據。本輪未執行 push、登入或遠端操作。

## 腳本介面變更

舊 shell 腳本保留為 Python 包裝器：init 只輸出計畫，quick-start 只預檢明確路徑，test-mdye-check 只查 PATH；失敗回傳非零。generate-unique-id 已停用，避免產生無效遠端 ID。Windows 直接使用 Python 指令，不需要 Bash。所有腳本不提權、不自動安裝、不修改登入或設定。

官方開發指南（來源見交付文件 docs/CLI_COMPATIBILITY.md） 是命令與平台流程的來源；部署管理者仍需確認適用版本及完整初始化命令。
