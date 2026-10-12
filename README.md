# niio Skills

適用於 niio 的台灣繁體中文 AI Agent 技能集合，涵蓋應用建置、資料查詢、API 串接及擴充開發。

## 更新通知與確認

每月 1 日台灣時間上午 9 點檢查上游版本（GitHub 排程可能延遲）。有新版本時建立 GitHub Issue，通知 @sigurd0414，附上提交紀錄、異動檔案及完整比較連結。沒有新版本不通知，同一版本不重複通知；Email 是否寄送依個人 GitHub 通知設定。

檢查流程不修改技能、不啟動同步。閱讀更新內容並決定採用後，開啟 [確認後同步並產生繁中技能](https://github.com/apsm-niio/niio-skills/actions/workflows/sync-upstream.yml)，按 **Run workflow**，選擇 `main`，在 `upstream_commit` 填入通知中的完整 40 位版本 SHA，再執行。同步只使用指定且存在於上游 main 歷史中的版本，並套用台灣用語、niio 設定及既有驗證。

不想更新時不執行即可；關閉通知 Issue 不會觸發同步。每日自動同步與推送後自動同步均已取消；調整本地轉換規則後，也需手動指定版本執行同步。

需要提前檢查時，可手動執行 [每月檢查上游更新（僅通知）](https://github.com/apsm-niio/niio-skills/actions/workflows/check-upstream.yml)。修改檢查流程本身時也會執行一次檢查。

第三方元件依各自授權條款使用，相關版權與授權聲明將隨附保留。
