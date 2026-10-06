# 應用級元資料、分組與 AI 助手

## 呼叫正規化

```bash
# 讀結構：應用資訊（含分組、工作表、自訂頁面）/ 我管理的應用清單
hap app info -a <appId>
hap app list-managed -o <orgId>

# 改應用名 / 描述 / 配色 / PC 導航樣式
hap app update <appId> -n "新名字" -d "新描述" \
  --icon-color "#2196F3" --nav-color "#1565C0" --pc-nav-style 1

# 側邊欄分組（section）
hap app add-section <appId> -n "運營"
hap app edit-section <appId> <sectionId> -n "市場"
hap app delete-section <appId> <sectionId> -y
hap app sort-sections <appId> <sectionId1> <sectionId2> <sectionId3>

# AI 助手（chatbot）
hap app chatbot create <appId> "客服助手" --section-id <sectionId> \
  --prompt "你是售後客服" --welcome-text "你好，有什麼可以幫你？" \
  --preset-question "如何退貨" --preset-question "查訂單狀態"
hap app chatbot get <chatbotId>
hap app chatbot rename <appId> <chatbotId> --section-id <sectionId> --name "售後助手"
hap app chatbot update-config <chatbotId> --welcome-text "歡迎諮詢" \
  --preset-question "新問題一" --preset-question "新問題二"
hap app chatbot delete <chatbotId> -a <appId> -y

# 應用回收站：刪掉的工作表 / 自訂頁 / AI 助手，帶刪除人和時間
hap app trash -a <appId>
hap app trash -a <appId> -k 訂單            # 按名稱過濾

# 分組內工作表排序（按順序傳完整 ID 清單）
hap app sort-worksheets <appId> <sectionId> <wsId1> <wsId2> <wsId3>

# 操作日誌：定位「這個改動是誰什麼時候做的」
hap app logs <appId> --kind app --start "2026-09-01 00:00:00"
hap app logs <appId> --kind record --ip <地址> --source-id <整合ID>
hap app log-archives                      # 超出近期視窗的按時段歸檔
hap app logs <appId> --archived-id <歸檔ID>
```

坑位提示：

- **新建分組會排到側邊欄最前面**，連建多個後順序是反的；建完用 `sort-sections` 傳**完整** section id 清單一次性修正順序。
- `app info` 回傳的分組條目裡 `type` 區分成員型別：0=工作表，1=自訂頁面，2=子分組。按名找元素時先看這個欄位。
- 改 `--pc-nav-style` 時圖示顯示預設隨樣式聯動；要精確控制用 `--display-icon`（3 位開關串，如 `011`）。
- 整應用從零建立不在本 skill 範圍（用 niio-mcp-app-builder）；這裡只編輯已存在的應用。
- chatbot 的 `--preset-question` 可重複傳，`update-config` 時是**整組替換**而非追加。
- 想讓 AI 起草助手設定，先 `hap app chatbot generate <appId> "<一句話描述>"` 拿到建議的名字/圖示/開場白/提示詞，再餵給 `create`。
- `app logs` 不指定 `--start/--end` 時預設**最近 30 天**；更早的要先 `app log-archives` 拿歸檔 id
  再用 `--archived-id` 查。`--kind` 取 `all|app|record|user`。
- **備份、角色改名這類操作失敗不再被當成功**：以前伺服器端用裸狀態碼表示「超限額」「重名」，CLI 照樣
  報成功；現在會按狀態碼判定並非零退出。

### 刪了之後怎麼確認真的刪掉了

工作表、自訂頁、AI 助手的刪除**預設都是進應用回收站**，不是抹掉。刪完用
`hap app trash -a <appId>` 核對：能看到它，說明刪成功了（還能還原）；看不到，才說明它根本沒被刪掉。

| 物件 | 預設 | 徹底刪除 |
|---|---|---|
| 自訂頁 | 進回收站 | `hap custom-page delete … --permanently` |
| AI 助手 | 進回收站 | `hap app chatbot delete … --permanent` |
| 工作表 | 進回收站 | **CLI 目前沒有出口**——只能在介面上從回收站裡徹底刪 |

兩個 `--permanent(ly)` 現在是真的徹底刪（先進回收站再按回收站記錄徹底刪，刪不掉會報錯並非零退出），
所以加了它之後 `app trash` 裡**看不到**才是正確結果。

## 資料字典

字典生成於 2026-06-10；未覆蓋的鍵以讀命令回傳的實際結構為準。

### app update 列舉與取值

| 鍵/選項 | 含義 | 值形態 |
|---|---|---|
| --pc-nav-style | PC 導航樣式 | int enum：0=經典，1=分組清單，2=卡片，3=樹形 |
| --display-icon | 圖示顯示開關 | 3 位 0/1 串（如 `011`），預設隨導航樣式 |
| --icon-color / --nav-color | 圖示色 / 導航欄色 | 十六進位制色值字串（如 `#2196F3`） |
| -n / -d | 應用名 / 描述 | string |

### app info 回傳的分組條目

| 鍵 | 含義 | 值形態 |
|---|---|---|
| type | 條目型別 | int enum：0=工作表，1=自訂頁面，2=子分組 |
| 其餘鍵 | 名稱、id、圖示等 | 以 `hap app info` 實際回傳為準 |

### chatbot 設定項

| 鍵/選項 | 含義 | 值形態 | 適用 |
|---|---|---|---|
| --prompt | 系統提示詞（定義助手行為） | string | create |
| --welcome-text | 開場白 | string | create / update-config |
| --preset-question | 預設問題（可重複，整組替換） | string ×N | create / update-config |
| --section-id | 所在導航分組 | string | create / rename / delete |
| --remark | 簡介 | string | create |
| --icon / --icon-color | 圖示與顏色 | string | create / rename |
| --permanent | 徹底刪除；不加就進應用回收站，用 `hap app trash` 能看到也能還原 | flag | delete |
| --lang | 起草語言型別，0=預設 | int | generate |
