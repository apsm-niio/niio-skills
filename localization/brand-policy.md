# niio 品牌例外政策

安裝用 skills 的顯示名稱使用 niio。`scripts/audit_brand.py` 分類文字中的識別字，未分類名稱及舊品牌檔名會阻擋同步。既有本地化檢查仍負責其他品牌字詞、連結及繁體用語。

| 類別 | 保留內容 | 理由 |
|---|---|---|
| 協定標頭 | HAP-Appid、HAP-Appkey、HAP-Sign | 保持 HTTP 協定相容 |
| 命令／套件 | hap、hap-cli、hap_cli、HAP_PROFILE | 與實際安裝命令、套件及設定一致；不得用作產品標題 |
| 遷移 | hap-plan.json、hap-context.json | 僅允許在指定 project_files.py 中讀取舊檔名 |
| 來源授權 | LICENSE、NOTICE 等法律文件與維護區上游網址 | 保留來源與授權，不當作產品展示名稱 |
| 非品牌 | shape、batchApprove、spc&happ | 一般識別字或既有協定值，不以子字串盲目替換 |

裸 HAP 及大小寫變體應改為 niio。CLI 指令中的小寫 hap 是明確例外；詞法檢查不能判定所有文字語意，新增顯示文案仍需人工審閱。圖片、登入頁、工具終端輸出與執行時畫面另需視覺驗收，此檢查不代表已完成那些驗收。

上游部署指引以 SHA 固定；來源改變即停止生成，人工審閱後才可更新覆寫。月度偵測仍僅通知，不自動接受上游變更。
