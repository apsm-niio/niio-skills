# 工作流（workflow）— 流程與節點基礎操作

操作物件分兩層：**流程**（process，一條工作流本身）與**節點**（node，流程內的步驟）。
節點的逐型別深度設定見 [nodes.md](nodes.md)；本篇只覆蓋流程級命令、節點增刪改名、觸發器設定。

**術語：PBP = 封裝業務流程（Packaged Business Process）。** 使用者說「封裝業務流程」「PBP」時，
一律對應 `workflow create --type pbp` + `batch-add --trigger-pbp`。

**全域規則**：改節點設定前先 `hap --json workflow node get <process_id> <node_id>` 匯出現狀，在真實結構上改，再寫回。

## 呼叫正規化

### 流程級

```bash
# 列出一個應用下的工作流（app_id 是位置參數，不是 --app-id）
hap workflow list <app_id> [-k 关键字] [--enabled|--disabled] [-n 50] [-p 1]

# 檢視流程詳情 / 節點結構
hap --json workflow get <process_id>
hap workflow structure <process_id>

# 新建流程。--company-id 可以不傳，組織由流程所屬的應用決定
hap workflow create -n "流程名" -a <app_id> --type worksheet

# 改名 / 描述 / 圖示；--version-name 給當前已釋出版本起名（版本清單裡就不是日期編號了）
hap workflow update <process_id> -n "新名" -d "描述" --icon-color "#2196F3"
hap workflow update <process_id> --icon-name <图标名>          # 圖示名見 niio CLI icon list
hap workflow update <process_id> --version-name "上线版"

# 複製。⚠️ -n 傳的是【字尾】，不是副本全名
hap workflow copy <process_id> -n "-2026版"       # 副本名 = 原名 + "-2026版"
hap workflow copy <process_id> --sub-process      # 把副本轉成子流程

# 刪除是三步，不是一步
hap workflow delete <process_id> -y     # 進回收站：停止執行但還在，可恢復
hap workflow restore <process_id>       # 從回收站恢復
hap workflow purge <process_id> -y      # 徹底刪除，無法恢復

# 釋出（啟用）/ 停用
hap workflow publish <process_id>
hap workflow publish <process_id> --disable

# 手動觸發一次（-s 傳源記錄 rowId）
hap workflow trigger <process_id> [-s <row_id>]
hap workflow trigger <process_id> --fields '[...]'   # 「啟動時要求填寫」的流程
hap workflow trigger <process_id> --debug '[...]'    # 待辦/簡訊/郵件都改發給自己，驗流程不驚動別人

# 版本與全域設定
hap workflow history <process_id>                       # 每行的 id 就是版本 id
hap workflow rollback <process_id> --version-id <版本ID> # 回到該版本
hap workflow rollback <process_id>                      # ⚠️ 不帶版本 id = 丟棄未釋出的草稿
hap workflow config-get <process_id>
hap workflow config-set <process_id> -c '{"allowRevoke": true}'

# 分組（流程清單左邊那一層）與跨應用移動
hap workflow groups <app_id>
hap workflow create-group <app_id> -n "订单相关"
hap workflow sort-groups <分组ID> <分组ID> <分组ID>
hap workflow delete-group <分组ID> -y      # 分組裡的流程不會被刪
hap workflow move <process_id> ...         # 移到別的應用，參數以 --help 為準
```

坑位提示：

- `hap workflow list <app_id>` 的應用 ID 既能當位置參數也能用 `-a`。新建的工作表觸發流程在觸發器
  繫結工作表之前**不會出現在該清單裡**——拿好 `create` 回傳的 `id`，別靠清單反查。
  `--kind` / `-k` / `--enabled|--disabled` 都是**取回清單後在本地篩**的，不影響分頁。
- **建完不等於建好，只有釋出會告訴你哪裡還差。** 節點一個個加都會成功，觸發器沒綁、填寫節點沒有
  可填欄位這類問題只在釋出時才暴露。加完節點順手 `publish` 一次。
- `publish` 只在流程真的啟用了才報成功，被拒時以非零狀態退出並指出是哪個節點不完整。最常見兩因：
  觸發器沒綁（見下文「觸發器設定」）、`fill_in` 節點一個可編輯欄位都沒有（`config.formProperties`
  全是 `readonly`/`hidden`）。收件人寫錯則是當場報錯，見 [nodes.md](nodes.md) 的 accounts 一節。
- **三處和字面意思不同**：`copy --name` 是追加在原名後的**字尾**；`copy --sub-process` 是把副本
  **變成**子流程（不是連同子流程一起復制）；`rollback` 不帶 `--version-id` 是**丟棄當前草稿**，
  不是回到上一個版本。
- `delete` 是**可撤銷**的（進回收站，用 `restore` 拿回來），只有 `purge` 是真的刪掉。
- `config-set` **只需要寫要改的項**，沒提到的設定保持原樣。注意 `triggerView` 是布林（觸發流程的人
  能不能看到這條流程記錄），不是檢視 ID。有幾處聯動不用自己管：關掉撤回時「哪些節點之後不允許撤回」
  會一併清掉；把「只能觸發指定工作流」改成別的模式時那份白名單也會一併清掉。

### 節點基礎（增 / 刪 / 改名 / 讀設定）

```bash
# 列出全部節點（拿 nodeId、typeId、連線關係）
hap --json workflow node list <process_id>

# 讀單個節點的完整設定（--type 傳該節點的 typeId，來自 node list）
hap --json workflow node get <process_id> <node_id> --type 6

# 追加節點：--after 必填，傳上游節點 ID（接在觸發器後就傳觸發節點 ID）
hap workflow node add <process_id> --type 6 -n "写入记录" --after <prev_node_id> \
  -a 1 --app-id <worksheet_id>

# 改名 / 刪除（刪除後兩側自動重連）
hap workflow node rename <process_id> <node_id> -n "新名"
hap workflow node delete <process_id> <node_id> -y

# 節點型別列舉速查
hap workflow node list-types    # 型別名 → 數字，就是 node add --type 認的值
hap workflow node types         # 連同資料節點的動作號一起列
```

坑位提示：

- **資料類節點（type 6 / 7 / 13）的目標工作表 `--app-id` 必須在 `node add` 時給定**；建好後再用 `node save` 補傳會被靜默丟棄，節點只能刪了重建。
- `node get` 建議總是帶 `--type <typeId>`（從 `node list` 讀），不同型別回傳的結構差異很大。
- 單獨改一個已存在節點的設定：`node get` 讀出 → 改你要改的鍵 → `node save` 整段寫回（節點 ID、連線、位置都保留）。具體每類節點的鍵表見 [nodes.md](nodes.md)。

### 批次建節點 + 觸發器設定（batch-add）

`node batch-add` 一次完成「綁觸發器 + 按順序建多個節點並配好」。節點間用別名互相引用，物理 ID 自動解析：

```bash
# 工作表觸發：繫結觸發表 + 事件，再順序建兩個節點
hap workflow node batch-add <process_id> \
  --trigger-worksheet <worksheet_id> --trigger-event create \
  --nodes '[
    {"nodeAlias":"find",  "nodeType":7, "config":{...}},
    {"nodeAlias":"write", "nodeType":6, "config":{...}}
  ]'

# 只配觸發器、不建節點：--nodes 傳空陣列
hap workflow node batch-add <process_id> --nodes '[]' \
  --trigger-schedule '{"repeat":"day","interval":1,"start_time":"2026-06-11 08:00"}'
```

觸發器相關選項按流程型別選用其一：

- `--trigger-worksheet` + `--trigger-event create|update|create_or_update|delete`（工作表事件型）；`--trigger-fields f1,f2` 把 update 觸發收窄到指定欄位；`--trigger-filter '<条件组JSON>'` 只放行滿足條件的記錄，條件結構 → [OperateCondition](../scripts/types/operate-condition.schema.json)。
- `--trigger-schedule '{repeat,interval,week_days,start_time,end_time,config}'`（定時型）。
- `--trigger-date '{worksheet,date_field_id,offset_type,offset_number,offset_unit,time,repeat}'`（按日期欄位型）。
- `--trigger-webhook '{"sample":{...}}'`（Webhook 型：用樣例請求體推匯入參結構）。
- `--trigger-pbp '{"inputs":[{name,type,required,alias,desc,default,options,children}]}'`（PBP/封装业务流程型：定義輸入參數。type 取 text/number/date/radio/checkbox/member/department/org_role/attachment/object/array/object_array，預設 text；radio 的 options 傳字串陣列；object_array 用 children 嵌一層子參數）。

```bash
# PBP：定義兩個輸入參數（建流程時 --type pbp）
hap workflow node batch-add <process_id> --nodes '[]' \
  --trigger-pbp '{"inputs":[
    {"name":"订单号","type":"text","required":true},
    {"name":"数量","type":"number"}
  ]}'
```

坑位提示：

- 新建的工作表觸發流程，**觸發器未繫結前無法釋出**——建完流程第一件事就是綁觸發器。
- 修「建到一半」的流程時不要重建：流程已存在就在原 process_id 上補——缺節點用 `node add` / `batch-add` 補，節點設定錯用 `node get` + `node save` 原位修，最後 `workflow publish`。需要精確控制分支內部拓撲的複雜重排不在此範圍。

## 資料字典

字典生成於 2026-06-10；未覆蓋的鍵以 `hap workflow node get` 回傳的實際結構為準。

### 觸發型別（`workflow create --type`）

`--type` 接受名稱或數字碼，優先用名稱：

| 值 | 含義 | 觸發器設定方式 |
|---|---|---|
| `worksheet`（1） | 工作表事件觸發 | `batch-add --trigger-worksheet/--trigger-event/--trigger-fields/--trigger-filter` |
| `scheduled`（5） | 定時（週期）觸發 | `batch-add --trigger-schedule` |
| `date`（6） | 按日期欄位觸發 | `batch-add --trigger-date` |
| `webhook`（7） | Webhook 觸發（外部 HTTP 請求） | `batch-add --trigger-webhook` |
| `pbp`（17） | **封裝業務流程（PBP）**，供其他流程/頁面按鈕呼叫；它不是 Webhook | `batch-add --trigger-pbp`；手動觸發用 `workflow trigger-pbp` |
| `staff` | 組織人員入職 / 離職 | 見 `batch-add --help` |
| `portal_user` | 外部使用者註冊、登入、被移除 | 見 `batch-add --help` |

也接受同義詞：`worksheet_event`、`schedule`、`date_field`、`staff_event`、`external_user`。
`workflow list --kind` 用的是同一套名字。

#### 觸發 PBP：先問它要什麼，再傳

```bash
hap workflow pbp-parameters <process_id>     # 這條流程要傳哪些入參；每行給出的欄位 ID 就是 controlId
hap workflow trigger-pbp <process_id> -a <app_id> --controls '[
  {"controlId": "<入参ID>", "value": "华东一区"},
  {"alias": "owner", "value": ["<成员accountId>"]}
]'
```

每一項用 `controlId`、參數別名（`alias`）或參數名認定一個入參。**參數名寫錯會當場報錯**並列出這條
流程實際接受哪些參數——不會靜默地帶著一串空參數把流程跑一遍。取值直接寫自然 JSON（陣列、數字、
布林都行），需要轉成文字時 CLI 會代勞。

### 釋出 / 啟用語義

| 鍵 / 操作 | 含義 | 值形態 |
|---|---|---|
| `enabled` | 流程是否已啟用（`workflow list` / `get` 回傳） | bool；`publish` 置 true，`publish --disable` 置 false |
| `publish` 結果 | 啟用成功與否 + 校驗診斷 | 失敗時輸出告警明細並非零退出；阻斷級告警必須修復後重發 |
| `workflow history` | 檢視釋出歷史 | `hap workflow history <pid>`，每行的 id 就是版本 id |
| `workflow rollback` | 回到某個版本 / 丟棄草稿 | 帶 `--version-id` 回到該版本；**不帶就是丟棄未釋出的草稿** |

### 節點型別 ID（`hap workflow node list-types` 完整列舉）

帶 → 的 8 類在 [nodes.md](nodes.md) 有逐鍵深度字典。

| typeId | 名稱 | 說明 |
|---|---|---|
| 0 | START | 觸發節點（每流程一個，不可增刪） |
| 1 | BRANCH | 分支閘道器 |
| 2 | BRANCH_ITEM | 分支項（條件掛在這層）→ nodes.md |
| 3 | FILL | 填寫 |
| 4 | APPROVAL | 審批 → nodes.md |
| 5 | CC | 抄送 → nodes.md |
| 6 | ACTION | 資料動作（增/改/刪記錄等）→ nodes.md |
| 7 | SEARCH | 查詢單條記錄 → nodes.md |
| 8 | WEBHOOK | 傳送 HTTP 請求 → nodes.md |
| 9 | FORMULA | 公式 |
| 10 | MESSAGE | 簡訊 |
| 11 | EMAIL | 傳送郵件 → nodes.md |
| 12 | DELAY | 延時 → nodes.md |
| 13 | GET_MORE_RECORD | 取得多條記錄 / 批次操作（`save-get-more` 設定） |
| 14 | CODE | 程式碼塊 |
| 15 | LINK | 取得連結 |
| 16 | SUB_PROCESS | 子流程 |
| 17 | PUSH | 介面推送 |
| 18 | FILE | 生成檔案 |
| 19 | TEMPLATE | 服務號訊息 |
| 20 | PBP | 呼叫封裝業務流程（在流程裡調一個已釋出的 PBP） |
| 21 | JSON_PARSE | JSON 解析 |
| 22 | AUTHENTICATION | API 身分驗證與授權 |
| 23 | PARAMETER | 參數 |
| 24 | API_PACKAGE | API 包 |
| 25 | API | 呼叫已整合 API |
| 26 | APPROVAL_PROCESS | 發起審批流程 |
| 27 | NOTICE | 站內通知 |
| 28 | SNAPSHOT | 記錄快照 |
| 29 | LOOP | 迴圈 |
| 30 | RETURN | 回傳 |
| 31 | AIGC | AI 生成 |
| 32 | PLUGIN | 外掛 |
| 33 | AGENT | AI Agent |
