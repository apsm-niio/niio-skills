# 本機整合與修復後回歸報告

2026-10-16，Windows 10.0.26200，Python 3.10.6、Node 22.12.0。所有資料為合成／mock，未連 niio。

|檢查|結果|界線|
|---|---|---|
|固定上游重新生成、品牌、授權、frontmatter|通過；87 個技能檔案、10 份 SKILL.md、8 個頂層技能隔離安裝逐檔一致|不代表工作階段已載入|
|完整 Python 整合輪|55 項：50 通過、4 error、1 failure，無 skip|5 項均為既有 Windows 連結限制，詳下|
|修復後受影響 Python|7/7 通過|安裝、更新、回復、意外 rename 中斷回復、自訂檔拒絕、掃描與外掛預檢／捕獲驗證|
|網站 Node|5/5 通過（整合輪）|模板未改；公開投影、秘密隔離與錯誤，無部署請求|
|外掛 Node|最終 2/2 通過|mock SDK 限量與目標檢查；缺值、0、無效數值、關聯筆數、選項解析|
|API／CLI／網站／外掛 capture|四通道最終 mock 通過；另有 HTTP／HTML／業務失敗／目標與形狀反例|只驗離線契約；真實來源需人工確認|
|CLI 編輯器 JSON Schema|10 份以 Ajv 8.17.1 編譯；edit-spec 正反例通過|不呼叫 hap、不套用操作，不證明部署相容|
|mdye 0.0.38|隔離 home/cwd、阻斷網路的 version 與 init/start/build/push help 通過|沒有 auth/init/start/build/push 本體執行；正式認證未讀|
|正式安裝核對|32 個受版控 builder 檔案仍與 0fa9c94 一致|Python 快取另計，未更新正式技能|

## 保留的環境失敗

- test_context_resolution_old_new_and_conflict：os.link WinError 5。
- test_equal_json_with_different_format_keeps_current_bytes：os.link WinError 5。
- test_old_pair_migrates_with_exact_backups_and_idempotence：os.link WinError 5。
- test_partial_migration_retries_without_overwrite：更早的備份 hardlink 被拒，後續目的檔不存在斷言失敗。
- test_symlink_lock_and_orphan_block：建立測試 symlink 時 WinError 1314，尚未進入產品的 symlink 防護。

沿用前輪最小診斷：原始 JSON 保留、CLI 回 1、鎖與暫存清理；無新檔、未降低保護。此輪同集合重現，不再重做不受修改影響的 Windows 診斷。沙箱預設 TEMP 新增的 rename 拒絕，改用工作區內隔離 TEMP 可通過安裝／回復；不是系統全域修復。

## 依賴與重現

本輪在新 venv 複製已固定版本的前輪依賴，使用同一 Python 3.10。jsonschema 安裝嘗試回報找不到分發版本，沒有完成安裝；改用本機 mdye 的 Ajv 及四個依賴，逐檔複製到隔離目錄並核對版本。CI 在其暫存目錄安裝相同固定版本，沒有修改使用者全域工具。

重現：依 README 建立隔離 venv、固定上游；執行 validate_release.py、unittest discover、兩個 Node test 檔、四個 capture fixture 及 validate-editspec.cjs。繁中 Windows 測試子程序設定 PYTHONUTF8=1；生成器檔案讀寫本身已明確 UTF-8。必要時僅對子程序設定 TEMP/TMP 為可寫隔離工作目錄。原始完整 logs 與 SHA256 manifest 在此次本機交付 outputs 中；真實應用證據不上傳公開 PR。

遠端部署、角色／同仁試用與歷史觸發日誌維持待驗收；以上沒有「全部部署通過」的結論。
