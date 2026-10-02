# 應用角色與許可權

## 呼叫正規化

```bash
# 列出角色 / 查看某角色完整权限明细
hap app role list -a <appId>
hap app role permissions <roleId> -a <appId>

# 粗粒度创建（permission-scope > 0，按整体范围授权）
hap app role create -a <appId> --name "运营" --description "运营人员" \
  --type 0 --permission-scope 20

# 细粒度创建（permission-scope 0 的推荐入口：逐表声明意图，未写到的部分自动补全为允许）
hap app role create-fine <appId> -n "区域经理" -d "只能看和改自己的记录" \
  --worksheet-permissions '[{"worksheetId":"<wsId>",
    "recordDataScope":{"read":20,"edit":20,"delete":0}}]' \
  --page-permissions '[{"pageId":"<pageId>","enable":true}]'

# 改名与改权限是两条独立命令，互不影响
hap app role rename <appId> <roleId> -n "新名字"
hap app role set-permissions <appId> <roleId> --permission-way 10

# 成员增删（平铺 id 选项，可重复传入，一次一个 id）
hap app role add-member <roleId> -a <appId> \
  --user-ids <accountId> --user-ids <accountId2> --department-ids <deptId>
hap app role remove-member <roleId> -a <appId> --user-ids <accountId>

# 删除角色
hap app role delete <roleId> -a <appId> -y

# 角色可访问的 AI 助手
hap app role set-chatbots <appId> <roleId> ...

# 加入申请：待处理列表 / 通过并分配角色 / 拒绝；把人从本应用所有角色里移除
hap app role pending <appId>
hap app role approve ...
hap app role reject ...
hap app role leave-all ...
```

> **失敗不再被當成功。** 改名、改許可權這類操作以前遇到重名等情況服務端返回的是裸狀態碼，CLI 會
> 照樣報成功；現在會按狀態碼判定並報錯退出。看到成功就是真的成功了，但**破壞性操作後仍建議
> `hap app role permissions <roleId> -a <appId>` 回讀確認**。

坑位提示：

- **`rename` 與 `set-permissions` 是兩條命令**。改名不會動許可權，改許可權不會動名字；不要試圖用一條命令同時做兩件事。
- `create` 用 `--permission-scope 0` 時**必須帶非空 `--worksheet-permissions-json`**，且每條目必須是完整結構（所有子物件齊全、工作表鍵名為 `id`）——缺子物件的條目會被拒絕。日常細粒度需求直接用 `create-fine`：它接受簡化意圖（鍵名 `worksheetId`），自動拉取該表的欄位與檢視把結構補全。
- `set-permissions` 適合粗粒度的 `--permission-way` 調整；`-P` 傳細粒度 JSON 的寫入路徑未充分驗證，細粒度需求優先用 `create-fine` 新建角色替換。
- 成員選項是**平鋪的 id 列表**（`--user-ids <id>` 重複傳即可），**與工作流收件人那套巢狀結構（type/entityId/accounts）完全無關**，不要往這裡塞物件。
- **排障正規化：成員登入後"看不到內容 / 某表打不開"**：
  1. `hap app role permissions <roleId> -a <appId>` 看該角色完整許可權；
  2. 若 `permissionScope` 為 0，逐項檢查 `worksheetPermissions` 裡對應表的 `recordDataScope.read` 是否為 0、`fieldPermissions` 是否把欄位 read 關了；
  3. 檢查 `pagePermissions` 裡目標自訂頁面的 `enable` 是否為 false；
  4. 檢查 `hideAppForMembers` 是否為 true（成員入口直接隱藏）；
  5. 確認成員確實在該角色裡（`hap app role list -a <appId>` 帶成員資訊）。

## 資料字典

字典生成於 2026-06-10；未覆蓋的鍵以讀命令返回的實際結構為準。

### 角色主體（create 的請求體 / permissions 的返回主體）

| 鍵 | 含義 | 值形態 |
|---|---|---|
| name | 角色名 | string（必填） |
| description | 角色描述 | string（必填） |
| hideAppForMembers | 對該角色成員隱藏整個應用 | bool |
| type | 角色型別，自訂角色固定 0 | int enum {0} |
| permissionScope | 粗粒度範圍：80=全部可檢視/編輯/刪除；60=檢視全部、僅編輯/刪除自己的；30=僅加入的項、僅編輯/刪除自己的；20=僅檢視；0=逐項細粒度 | int enum {0,20,30,60,80} |
| globalPermissions | 應用級動作開關，僅 permissionScope > 0 時生效 | object，見下表 |
| worksheetPermissions | 逐表許可權明細，僅 permissionScope == 0 時生效 | array，見下表 |
| pagePermissions | 逐自訂頁面可見性，僅 permissionScope == 0 時生效 | `[{id:"<pageId>", enable:bool}]` |

### globalPermissions（8 個布林開關，全部必填）

| 鍵 | 含義 | 值形態 |
|---|---|---|
| addRecord | 新增記錄 | bool |
| share | 公開分享檢視與記錄 | bool |
| import | 匯入 | bool |
| export | 匯出 | bool |
| discuss | 討論 | bool |
| systemPrint | 系統列印 | bool |
| attachmentDownload | 附件下載 | bool |
| log | 檢視記錄日誌 | bool |

### worksheetPermissions[] 條目（scope 0 時每條必須完整）

| 鍵 | 含義 | 值形態 |
|---|---|---|
| id | 工作表 id（注意鍵名是 `id`，不是 `worksheetId`） | string |
| recordDataScope | 行級讀/改/刪範圍 | `{read, edit, delete}`，各為 int enum：0=無許可權，20=僅自己的，30=自己及下屬的，100=全部 |
| worksheetActions | 表級動作 | `{shareView, import, export, discuss, batchOperation}` 全 bool |
| paymentActions | 支付 | `{pay: bool}` |
| recordActions | 記錄級動作 | `{add, share, discuss, systemPrint, attachmentDownload, log}` 全 bool |
| recordPermissionInViews | 按檢視的行許可權 | `[{viewId, read, edit, delete}]`（bool） |
| fieldPermissions | 按欄位的許可權 | `[{id:"<controlId>", add, read, edit, decrypt?}]`（bool；decrypt 可選） |

`create-fine` 意圖補全預設值：recordDataScope → read/edit/delete 全 100；worksheetActions → 僅 discuss 為 true；recordActions → add/discuss/attachmentDownload 為 true，其餘 false；fieldPermissions → 每欄位 read/edit/add true、decrypt false；檢視 → 全部可讀（除非給了允許清單）。`create-fine` 的意圖 JSON 用 `worksheetId` 作鍵，落庫時轉換為 `id`。

### set-permissions（粗粒度）

| 鍵 | 含義 | 值形態 |
|---|---|---|
| permission-way | 角色粗型別 | int enum：0=自訂，10=只讀，50=成員，100=管理員 |
| permissions (-P) | 細粒度許可權 JSON | object（寫入路徑未充分驗證，慎用） |

### add-member / remove-member 平鋪 id 選項

均為可重複的字串選項（一次一個 id），與工作流收件人結構無關。

| 選項 | 含義 | 適用 |
|---|---|---|
| --user-ids | 使用者（帳號）id | add / remove |
| --department-ids | 部門 id | add / remove |
| --department-tree-ids | 部門樹 id（含子部門） | add / remove |
| --job-ids | 職位 id | add / remove |
| --project-organize-ids | 組織角色 id | 僅 add |
| --org-role-ids | 組織角色 id | 僅 remove |
