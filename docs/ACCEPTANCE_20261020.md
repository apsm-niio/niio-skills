# niio-skills 2026-10-20 驗證與交付結果

本文件補充並更新 2026-10-19 的 ONBOARDING_PROGRESS.md 快照。技能交付基準為 `1d75354d251bf94d9dabf314f8f0c66b55d0e25c`；不要把部署端未驗收項目視為已完成。

## 已完成

- PR #3、#4 的來源、認證與新使用者指引修正已審閱並合併；PR #5 新增 Windows 實際連結 CI，亦已合併。
- 使用已確認的測試應用臨時 AppKey／Sign，對更正後工作表執行一次 V3 GET：HTTP 200、application/json、success=true、worksheetId 相符，18 欄均提供名稱與型別。禁止重新導向及自動重試。未查詢或寫入業務列，未將密鑰公開。這僅結清指定 V3 結構讀取，不抵充列表／CLI／SDK。
- 八個本機正式技能更新前皆符合 68d03b0 完整基準；更新後 87/87 檔與來源及安裝 receipt 相符，八份舊版備份與 receipt 相符。
- 固定上游來源重新生成通過，8 技能、87 檔、品牌與授權檢查及隔離安裝一致。
- Node 網站／外掛離線測試 7/7，編輯器 schema 10 項通過；四個通道 fixture 驗證通過，均僅為 mock。

## Windows 原五項

[Windows 實際連結 CI](https://github.com/apsm-niio/niio-skills/actions/runs/39382118490)：原 test_project_files.py 的 9/9 全部通過，包含原先受阻的四項硬連結遷移及一項符號連結防護。日誌確認未 skip。該測試及遷移實作相對既有基準未修改，沒有降低保護。

本機 Codex Windows 沙箱仍出現 WinError 5／1314；增加測試目錄存取權仍未改變。安裝完整依賴後本機 Python 測試為 60/65 通過，其餘正是上述五項，不能把本機結果寫成全綠。[PR #5 的整合 CI](https://github.com/apsm-niio/niio-skills/actions/runs/39382118430) 已通過。Windows runner 的證據不代表本機沙箱權限已解除；本次未改系統 ACL 或開發人員模式。

## CLI

在隔離 Python 環境安裝固定 hap-cli 0.9.10；版本、guide、guide setup、auth login --help、worksheet record list --help 均成功。隔離設定明確關閉自動更新及自動登入，未變更使用者全域設定。現有一般帳號設定未找到，且缺本部署確認的 CLI 登入入口／profile，因此遠端查詢尚未驗收。AppKey／Sign 與 MCP PAT 沒有轉作 CLI 登入。

## 仍需部署條件

|項目|尚缺條件與原因|
|---|---|
|通用工作流工具錯誤|缺事件版本 handler、gateway／引擎日誌及 execution ID，不能判定 Unexpected response type 的來源或請求是否已執行。未再次觸發。|
|網站真實 API／部署|V3 結構成功不包含列表契約、公開資料集、發布條件、欄位白名單與網站部署目標；不可自行公開測試／內部資料。|
|檢視外掛／SDK|缺平台產生的初始化參數與獲准測試檢視，無法實際掛載並核對資料。|
|一般成員／主管角色|缺兩個獨立測試身分；管理員成功不能證明角色允許與禁止行為。|
|後端防重複／遠端建置恢復|缺隔離案例及引擎執行追蹤；按鈕不能再點不證明後端冪等。|
|兩份舊 PowerShell 授權腳本|對已知本機 Documents、OneDrive、.codex 搜尋指定檔名未找到；不將未審查來源納入交付。|
|部署網址多餘句點／舊品牌|屬部署設定或伺服器生成內容；本機技能修正不會改產品 UI。V3 回傳部分系統欄位亦仍為簡體。|

重新開啟 Codex 工作階段後才可驗收新版技能載入。臨時 API 授權完成用途後可撤銷。部署端項目待取得必要材料才能繼續，不能宣稱整套遠端能力全部完成。
