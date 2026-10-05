# 工作流節點深度設定 — 8 類高頻節點逐鍵字典

覆蓋 8 類高頻節點：ACTION(6)、SEARCH(7)、APPROVAL(4)、CC(5)、WEBHOOK(8)、EMAIL(11)、DELAY(12)、BRANCH 閘道器(1) + 分支項(2)。
流程級與節點增刪見 [workflows.md](workflows.md)。

**全域規則**：改節點設定前先 `hap --json workflow node get <process_id> <node_id>` 匯出現狀，在真實結構上改，再寫回。**讀出來的結構就是寫回去的結構**——只改你理解的鍵，其餘原樣保留。

## 兩層寫法：先分清 batch-add 高層 與 node save wire 層

- **高層**：`hap workflow node batch-add --nodes '[{"nodeAlias":…, "nodeType":…, "config":{…}}]'`
  一次建好整條流程，`nodeType` 用**名字**（`create_record` / `approve` / `fill_in` / `notice`…），
  收件人用 `{"kind": …}` 形狀（見下）。**建新流程優先用它。**
- **wire 層**：`node add` / `node save` 是單節點底層操作，`--type` 用**數字**型別號，收件人是
  `{"type":1|2|6|7, entityId, roleId}` 形狀。**本文 §ACTION 以下的逐鍵字典都是 wire 層**，
  用於改一個已經存在的節點。

數字型別號和資料節點的動作號不用猜：`hap workflow node list-types`（型別名 → 數字）、
`hap workflow node types`（連動作號一起列）。

### 高層收件人：`config.accounts` 的 kind 形狀

`batch-add --nodes` 裡，通知、抄送、郵件、審批、填寫這些節點的收件人都寫在 `config.accounts`，
每項是 `{"kind": …, 這個 kind 需要的鍵}`：

| kind | 還要給什麼 | 指誰 |
| --- | --- | --- |
| `user` | `userId` | 指定的人 |
| `role` | `appId` + `roleId` | 應用角色 |
| `department` | `departmentId` | 一個部門 |
| `job` | `jobId` | 一個職位 |
| `orgRole` | `orgRoleId` | 組織角色 |
| `field` | `fieldId`（可選 `node`） | 某條記錄上的成員 / 部門欄位 |
| `owner` / `triggerUser` | 無（可選 `node`） | 觸發這條流程的人 |
| `supervisor` | 無（可選 `node`） | 觸發者的直屬上級 |
| `email` | `email` | 一個外部郵箱地址（郵件節點用） |

> 🚨 **鍵名必須和 kind 對得上，寫錯會當場被拒絕**並告訴你缺哪個鍵。把指定成員寫成
> `{"kind":"user","id":"…"}`（最自然的猜法，也是 CLI 別處的寫法）會直接得到「kind 為 user 的
> 收件人需要 userId」，而不是建出一個看著沒問題、到釋出才出事的節點。`role` 少給 `appId`、
> `field` 把欄位 ID 放到別的鍵上，同樣當場報錯。

### 高層保留別名

**四個別名是保留字，不能用作 `nodeAlias`**：`trigger`、`sub_trigger`、`approval_trigger`、
`approval_start`——它們分別指觸發記錄、子流程目前遍歷到的那條記錄、審批區塊內部的發起記錄。
佔用了它們，後面所有引用都會指到錯的節點上；CLI 在動手建之前就會拒絕，不會留半截流程。

`nodeAlias` 是你給節點起的短名，後面的節點用它引用前面的節點；觸發記錄本身固定用 `trigger` 引用。

### 填寫節點發布不過去

`fill_in` 的 `config.formProperties` 逐欄位給權限，取值 `editable`、`required`、`readonly`、
`hidden`。**一個可編輯欄位都沒有（全是隻讀或隱藏）就釋出不了**，而這隻有釋出才會告訴你。

## 呼叫正規化（wire 層）

寫回設定走三條路，按節點型別選：

| 節點型別 | 命令 |
|---|---|
| ACTION(6) | `hap workflow node save-action`（專用快捷命令） |
| SEARCH(7) | `hap workflow node save-search`（專用快捷命令） |
| GET_MORE_RECORD(13) | `hap workflow node save-get-more`（專用快捷命令） |
| 其餘所有型別（含 APPROVAL/CC/WEBHOOK/EMAIL/DELAY/BRANCH） | `hap workflow node save <pid> <nid> --type <typeId> -c '<整段設定JSON>'` |

通用坑位（先讀完再動手）：

- **accounts 收件人編碼是頭號坑**：`type` 欄位反直覺——`1`=固定使用者（accountId 放在 `roleId` 裡，不是 entityId！）、`2`=應用角色（`entityId`=應用 ID、`roleId`=角色 ID）、`6`=動態引用（觸發者 `roleId:"uaid"`；成員欄位引用放該欄位的 controlId）、`7`=郵箱字面量（放 `entityId`）。編碼錯會讓收件人顯示為「已刪除」、流程無法釋出。完整結構 → [WorkflowAccounts](../scripts/types/workflow-accounts.schema.json)。
- **條件分兩種寫法，看你走哪條命令**：
  - `save-action` / `save-search` / `save-get-more` 的 `--condition` 用統一篩選寫法
    `{"logic":"and","items":[{"field":"<列>","op":"eq","value":"<值>"}]}`——列寫 ID、別名或標題都行，
    型別自動查出來。工作流條件專屬兩樣：`node` 指明這一列屬於哪個上游步驟，`value` 寫成物件
    （`{"kind":"field","node":…,"fieldId":…}` 跟另一步驟的列比，`{"kind":"systemField","fieldId":"nowTime"}`
    跟系統值比）。**工作流沒有 `between`**，寫 `gte` + `lte` 兩條。可用的比較方式見 `hap guide record filter`。
  - `node save -c` 裡的條件只收**儲存形態**：`operateCondition` 是二維陣列（外層 OR、內層 AND），
    欄位鍵是歷史拼寫 `filedId`（不是 `fieldId`——寫成 `fieldId` 會被靜默忽略，條件永遠不命中）。
    完整結構 → [OperateCondition](../scripts/types/operate-condition.schema.json)。
    🚨 **在 `node save -c` 裡寫統一寫法是靜默失效的**：放進 `operateCondition` 會被當場拒絕（提示它要
    二維陣列），但放進 `filter` / `condition` 鍵時**命令報成功、條件卻被清空**，分支從此對所有記錄放行。
    要用統一寫法就走上面三個快捷命令的 `--condition`。
  - **讀回時條件在哪個鍵**，跟寫入用的鍵不是一回事：查詢 / 資料 / 多條記錄節點讀回在 `filters`（每組帶
    `spliceType`），分支項讀回在 `conditions`；`operateCondition` 只是寫入時用的鍵。
- 欄位寫入項（fields）的動態值用 `$<nodeId>-<fieldId>$` 模板引用上游節點的欄位，nodeId 來自 `node list`。完整結構 → [WorkflowFieldWrite](../scripts/types/workflow-field-write.schema.json)。
- 資料 / 查詢 / 取得多條記錄節點的目標工作表用 `node add --app-id` 給定，**也可以稍後在設定節點時再設定**。
- `node add` 還有幾個位置與搬運選項：`--gateway parallel|exclusive`（分支節點走每條路還是隻走第一條
  符合條件的）、`--result-branch`（哪條是結果分支）、`--place left|right|withdraw`（新節點相對它
  跟隨的那個節點放哪）、`--copy`（把若干節點一併複製到新節點旁，配 `--move` 是移動、配
  `--copy-whole-branch` 整條分支一起帶走）。
- 資料節點的動作號（`-a/--action-id`）不用記：`hap workflow node types` 會連型別號一起列出來。
- **長尾節點型別的處理**：本文未覆蓋的型別（公式、程式碼塊、子流程、站內通知……）一律先 `hap --json workflow node get <pid> <nid> --type <typeId>` 讀現狀，照著回傳結構的形狀改寫要改的鍵，再用 `node save` 整段寫回。不要憑空構造設定。
  - **程式碼塊節點(14)**：`node save --type 14 --config '{"code":"return { ok: 1 };"}'` —— **直接傳原始碼，
    不要自己做任何編碼轉換**（不要 base64）。原始碼裡的 Tab 會統一成 4 個空格，與介面裡儲存的效果一致；
    `node get` 讀出來的 `code` 是明文，改完原樣傳回。試跑用 `node test-code <pid> <nid> -c "…"`，
    `--language` 指定按哪種語言跑（不傳就用節點自己的設定）。可複用片段用 `node create-code-template`
    存、`node code-templates` 找，**按語言和歸屬兩項找**（`--scope mine` / 不加 `--scope` 是內建示例）。
  - **AI 節點**：`node test-ai` 試跑，`--kind` 說明它做什麼（`text` 寫文字 / `object` 填結構化結果，
    這時必須配 `--outputs` 描述要填哪些欄位 / `agent` 執行助手）。`--model` 要的是本組織已設定的
    **某個模型的 ID**，不是 `gpt-4` 這樣的名稱——用 `node get` 讀節點能看到它目前用哪一個。
  - **站內通知(27)** 有兩個易漏點：收件人寫「觸發者」用 `accounts:[{"type":6,"roleId":"triggeraid"}]`；且設定裡**必須保留 `flowNodeMap["106"]` 推送子塊**（read-modify-write 時原樣帶回，刪了釋出會報錯）。無現成模板時可先 `node get` 一個同流程已有的 27 節點照形改寫。

### 輔助命令（讀結構、查可選項）

```bash
hap workflow node controls <pid> <nid>       # 可用於節點設定的工作表欄位
hap workflow node form-property <pid> <nid>  # 節點表單屬性
hap workflow node sub-processes <pid>        # 子流程節點可選的子流程
hap workflow node json-to-controls ...       # 把 JSON 轉成工作流欄位
hap workflow node desc <pid> <nid> ...       # 設定節點說明與別名
hap workflow node test-webhook <pid> <nid>   # 「傳送自訂請求」節點的測試 API
```

### ACTION(6) — 增 / 改 / 刪記錄

```bash
# 在目標表新增一條記錄，兩個欄位：一個靜態值、一個引用觸發記錄的欄位
hap workflow node save-action <pid> <nid> -a 1 --app-id <worksheet_id> \
  -f '[{"fieldId":"<狀態列位id>","type":11,"fieldValue":"<選項key>"},
       {"fieldId":"<標題欄位id>","type":2,"fieldValue":"$<trigger_node_id>-<標題欄位id>$"}]'

# 按條件更新上游節點指向的記錄
hap workflow node save-action <pid> <nid> -a 2 --app-id <worksheet_id> \
  -s <source_node_id> \
  -f '[{"fieldId":"<金額欄位id>","type":6,"fieldValue":"100"}]' \
  --condition '{"logic":"and","items":[{"field":"<金額欄位>","op":"gt","value":0}]}'
```

### SEARCH(7) — 查詢單條記錄

```bash
# 按條件查一條，查不到就新建（--not-found 1），新建時寫入 fields
hap workflow node save-search <pid> <nid> -a 406 --app-id <worksheet_id> \
  --condition '{"logic":"and","items":[{"field":"<編號欄位>","op":"eq",
       "value":{"kind":"field","node":"<trigger_node_id>","fieldId":"<編號欄位id>"}}]}' \
  --sorts '[{"controlId":"ctime","controlType":16,"isAsc":false}]' \
  --not-found 1 \
  -f '[{"fieldId":"<編號欄位id>","type":2,"fieldValue":"$<trigger_node_id>-<編號欄位id>$"}]'
```

`-a` 取值：`406`=按條件查工作表、`421`=查到並更新、`422`=查到並刪除、`407`=從多條記錄節點取一條（配 `-s <多條節點id>`）。多條 / 批次場景換 `save-get-more`（`-a 400`=查多條、`412`=批次更新、`413`=批次刪除，選項同形，另有 `--limit '{"fieldValue":"100"}'` 限制條數）。

### APPROVAL(4) / CC(5) / WEBHOOK(8) / EMAIL(11) / DELAY(12) / BRANCH(2) — 通用 save

這幾類沒有專用快捷命令，統一走 read-modify-write + `node save`：

```bash
# 1. 匯出現狀
hap --json workflow node get <pid> <nid> --type 4 > /tmp/node.json
# 2. 在 /tmp/node.json 的真實結構上只改要改的鍵（如 accounts、countersignType）
# 3. 整段寫回
hap workflow node save <pid> <nid> --type 4 -c "$(cat /tmp/node.json | jq '.<設定所在層>')"
```

一次性給一個 CC 節點換收件人（寫成應用角色）的最小示例：

```bash
hap --json workflow node get <pid> <nid> --type 5   # 先讀，確認其餘鍵
hap workflow node save <pid> <nid> --type 5 -c '{
  "selectNodeId": "<trigger_node_id>",
  "accounts": [{"type": 2, "entityId": "<app_id>", "roleId": "<role_id>"}],
  "sendContent": "有新記錄需要您關注",
  "showTitle": true
}'
```

> `-c` 傳的是設定 JSON；`node get` 回傳中與設定無關的只讀鍵（id、連線等）不必回傳，但**所有設定鍵都應保留原值回傳**，漏鍵可能被視為清空。

## 資料字典

字典生成於 2026-06-10；未覆蓋的鍵以 `hap workflow node get` 回傳的實際結構為準。

值形態分三級：① 標量/列舉（直接列值）；② 簡單結構（一句話描述）；③ 複雜結構（連結到 schema，或以 `node get` 實際回傳為準）。

### ACTION(6)

| 鍵 | 含義 | 值形態 |
|---|---|---|
| `actionId` | 操作子型別 | ① `"1"`=新增記錄 `"2"`=更新記錄 `"3"`=刪除記錄 `"5"`=新建並關聯 `"6"`=重新整理單條 `"20"`=關聯記錄 `"411"`=批次動作 `"412"`=批次更新 `"413"`=批次刪除 `"415"`=重新整理多條 |
| `appId` | 目標工作表 ID（必須在 `node add` 時設定） | ① 字串 ID |
| `appType` | 目標物件類別 | ① int：1=工作表 2=任務 5=迴圈 6=日期 7=Webhook 8=自訂動作 |
| `selectNodeId` | 該動作作用的記錄來自哪個上游節點 | ① 節點 ID 字串 |
| `fields` | 新增/更新時的欄位寫入 | ③ → [WorkflowFieldWrite](../scripts/types/workflow-field-write.schema.json) 陣列 |
| `operateCondition` | 限定作用記錄的過濾條件 | ③ → [OperateCondition](../scripts/types/operate-condition.schema.json) |
| `sorts` | 排序（取第一條語義） | ③ → [SortItem](../scripts/types/sort-item.schema.json) 陣列 |
| `executeType` | 無匹配資料/失敗時的行為 | ① 0=中止（或走「無資料」分支） 1=新增一條後繼續 2=跳過繼續 |
| `random` | 忽略排序隨機取 | ① bool |
| `destroy` | 刪除操作跳過回收站（硬刪） | ① bool |
| `sourceAppId` / `sourceAppType` | 跨表複製/關聯時的來源物件 | ① 字串 ID / int（同 appType） |
| `filters` | 批次操作的「條件+排序」分組 | ③ 元素內的條件同 OperateCondition 形狀；以 `node get` 實際回傳為準 |

### SEARCH(7)

查詢變體（406/420/421/422）在建節點時已固定，save 時不傳 `actionId`（專用命令的 `-a` 只用於選參數組合）。

| 鍵 | 含義 | 值形態 |
|---|---|---|
| `appId` | 被查詢的工作表 | ① 字串 ID |
| `selectNodeId` | 提供查詢輸入的上游節點 | ① 節點 ID 字串 |
| `operateCondition` | 查詢條件 | ③ → [OperateCondition](../scripts/types/operate-condition.schema.json) |
| `sorts` | 排序——第一條命中 | ③ → [SortItem](../scripts/types/sort-item.schema.json) 陣列 |
| `random` | 忽略排序隨機取 | ① bool |
| `executeType` | 查不到時 | ① 0=中止或走「無資料」分支 1=新建一條後繼續 2=跳過繼續 |
| `fields` | `executeType=1` 時新建記錄的欄位值 | ③ → [WorkflowFieldWrite](../scripts/types/workflow-field-write.schema.json) 陣列 |
| `findFields` | 連結解析/匹配模式下作為查詢鍵的欄位 | ③ 以 `node get` 實際回傳為準 |
| `link` | 記錄連結來源值（連結解析變體） | ② 字串或欄位引用，待解析的記錄 URL |
| `destroy` | 「查到並刪除」變體：硬刪跳過回收站 | ① bool |
| `returnNew` | 後續節點看到的快照 | ① `false`=本節點時刻的資料副本，`null`=每次使用重新取最新 |
| `ignoreError` | `executeType=1` 時插入失敗（唯一索引衝突）也繼續 | ① bool |
| `execute` | 透傳標誌，按讀到的原值回傳 | ① bool |
| `filters` | 「條件+排序」分組 | ③ 同 ACTION 的 filters |
| `flowNodeMap` | 內嵌子節點設定（如查不到時的新建分支） | ③ 以 `node get` 實際回傳為準 |

### APPROVAL(4)

| 鍵 | 含義 | 值形態 |
|---|---|---|
| `accounts` | 審批人 | ③ → [WorkflowAccounts](../scripts/types/workflow-accounts.schema.json) 陣列 |
| `multipleLevelType` | 審批人模式 | ① 0=指定審批人；1/2=逐級向上（變體）；3/4=逐級向下（變體）；11=由上一審批人從候選範圍圈定 |
| `multipleLevel` | 逐級模式的層數 | ① int，-1=直到最高層 |
| `countersignType` | 多人審批方式 | ① 3=或籤（一人透過即可） 1=會籤（全員透過） 2=會籤（一人透過即透過，否決需全員） 4=會籤（按透過比例） |
| `condition` | `countersignType=4` 的透過比例 | ① 字串 `"10"`…`"100"` |
| `operationTypeList` | 啟用的附加操作（轉交/加簽/退回/列印…） | ② int 清單，按 `node get` 讀到的現值增刪 |
| `ignoreRequired` | 必填欄位為空也允許透過 | ① bool |
| `isCallBack` | 退回後允許重新審批（回撥） | ① bool |
| `callBackType` / `callBackMultipleLevel` / `callBackNodeType` / `callBackNodeIds` | 回撥方式 / 深度 / 退回到哪些節點 | ② int / int / int / 節點 ID 清單；照讀到的原值改 |
| `formProperties` | 審批時每個欄位的檢視/編輯/必填/隱藏 | ③ 以 `node get` 實際回傳為準 |
| `passBtnName` / `overruleBtnName` / `returnBtnName` | 自訂按鈕文案 | ① 字串 |
| `auth` | 透過/否決時的簽名、附件要求 | ③ `{passAuth:[], overruleAuth:[]}`，以實際回傳為準 |
| `batchApprove` / `fastApprove` | 允許批次審批 / 免開啟記錄快速審批 | ① bool |
| `allowUploadAttachment` | 審批意見允許傳附件 | ① bool |
| `schedule` | 超時自動透過 / 升級提醒 | ③ 以 `node get` 實際回傳為準 |
| `passSendMessage` / `passMessage` / `overruleSendMessage` / `overruleMessage` | 透過/否決時通知發起人 + 模板文案 | ① bool / 字串 |
| `encrypt` | 審批操作需身份驗證 | ① bool |
| `operationUserRange` | 各操作（轉交/轉審…）允許的人員範圍 | ③ 操作碼 → Accounts 陣列的對映 |
| `opinionTemplate` | 預置審批意見模板 | ③ 以 `node get` 實際回傳為準 |
| `flowNodeMap` | 內嵌通知子節點設定 | ③ 以 `node get` 實際回傳為準 |
| `userTaskNullMap` | 審批人為空時的處理 | ③ 以 `node get` 實際回傳為準 |
| `candidateUserMap` | `multipleLevelType=11` 的候選範圍 | ③ 以 `node get` 實際回傳為準 |
| `addNotAllowView` | 審批人無檢視權限時隱藏記錄 | ① bool |
| `signOperationType` | 加簽的先/後順序行為 | ① int，照讀到的原值改 |
| `explain` | 展示給審批人的說明文字 | ① 字串 |

### CC(5)

| 鍵 | 含義 | 值形態 |
|---|---|---|
| `accounts` | 抄送物件 | ③ → [WorkflowAccounts](../scripts/types/workflow-accounts.schema.json) 陣列 |
| `sendContent` | 通知正文（支援欄位引用） | ① 字串 |
| `selectNodeId` | 被抄送記錄來自哪個節點 | ① 節點 ID 字串 |
| `formProperties` | 收件人可見的欄位範圍 | ③ 以 `node get` 實際回傳為準 |
| `viewId` | 用哪個檢視呈現記錄給收件人 | ① 檢視 ID 字串 |
| `addNotAllowView` | 收件人無檢視權限時限制檢視 | ① bool |
| `showTitle` | 訊息裡顯示記錄標題（`sendContent` 為空時強制 true） | ① bool |
| `flowNodeMap` | 內嵌子節點設定 | ③ 以 `node get` 實際回傳為準 |

注意：`smsContent` / `templateId` 屬於簡訊節點（type 10），不是 CC 的鍵。

### WEBHOOK(8)

| 鍵 | 含義 | 值形態 |
|---|---|---|
| `sendContent` | **請求 URL**（支援欄位引用）——不要找 `url` 鍵，它不存在 | ① 字串 |
| `method` | HTTP 方法 | ① 1=GET 2=POST 3=PUT 14=DELETE 5=HEAD 6=PATCH |
| `headers` | 請求頭（空名會被過濾） | ② `[{name, value}]` |
| `contentType` | 請求體編碼 | ① 1=x-www-form-urlencoded 2=raw 3=raw 子變體 4=form-data 5=binary |
| `body` | 原始請求體（contentType 2/3） | ① 字串 |
| `formControls` | form-data / urlencoded 的鍵值參數 | ③ 以 `node get` 實際回傳為準 |
| `settings` | 超時、重試等傳輸設定 | ③ 以 `node get` 實際回傳為準 |
| `successCode` | 視為成功的狀態碼 | ① 字串/int |
| `errorMap` | 狀態碼 → 自訂錯誤訊息（兩側都要填） | ② 狀態碼到訊息的對映 |
| `errorMsg` | 預設錯誤訊息 | ① 字串 |
| `executeType` | 超時/失敗時 | ① 0=中止 2=跳過繼續（此節點沒有 1） |
| `authId` | 關聯的身分驗證與授權賬戶 ID | ① 字串 ID |
| `ignoreValueEmpty` | 跳過取值為空的參數 | ① bool |
| `disabledCode` | 判定成功時忽略 HTTP 狀態碼 | ① bool |
| `selectNodeId` | 欄位替換的資料來源節點 | ① 節點 ID 字串 |
| `testMap` | 已儲存的測試參數值 | ③ 以 `node get` 實際回傳為準 |

正式儲存前可用 `hap workflow node test-webhook <pid> <nid> -u <url> -m POST -b '<body>'` 幹跑。

### EMAIL(11)

| 鍵 | 含義 | 值形態 |
|---|---|---|
| `actionId` | 傳送模式 | ① `"202"`=標準（抄送人互相可見） `"201"`=一對一單發 |
| `accounts` | 收件人（至少一個） | ③ → [WorkflowAccounts](../scripts/types/workflow-accounts.schema.json) 陣列（郵箱字面量用 type 7） |
| `ccAccounts` | 抄送人（僅標準模式） | ③ 同上 |
| `fields` | 郵件內容——**主題和正文都在這裡**，沒有頂層 `subject`/`content` 鍵 | ② `[{fieldId:"subject", fieldValue:"..."}, {fieldId:"content", fieldValue:"...", isRichText:bool}]` |
| `appType` | 透傳鍵，按讀到的原值回傳 | ① int |

### DELAY(12)

| 鍵 | 含義 | 值形態 | 適用 |
|---|---|---|---|
| `actionId` | 延時模式 | ① `"300"`=延到某個日期時刻 `"301"`=延時一段時長 | 全部 |
| `fieldValue` / `fieldNodeId` / `fieldControlId` | 目標日期：靜態值或欄位引用（頂層內聯） | ② 靜態填 `fieldValue`；引用欄位填 `fieldNodeId`+`fieldControlId` | 300 |
| `fieldControlType` / `fieldControlName` | 被引用日期控制元件的型別/名（型別 16=日期時間，自帶時間） | ① int / 字串 | 300 |
| `executeTimeType` | 相對目標日期的時間錨點——鍵名是它，**沒有 `executeTime` 這個鍵** | ① 0=當時 1=之前 2=之後 | 300 |
| `time` | 當天的時刻 `"H:mm"`（預設 `"8:00"`；日期時間控制元件自帶時間時置 null） | ① 字串 | 300 |
| `number` / `unit` | 前移/後移的量與單位 | ① int / 1=分鐘 2=小時 3=天 | 300 |
| `day` | 天數標記；`executeTimeType != 0` 時固定為 1 | ① int | 300 |
| `numberFieldValue` / `hourFieldValue` / `minuteFieldValue` / `secondFieldValue` | 時長的天/時/分/秒，各自可靜態或引用欄位 | ② 每個都是 `{fieldValue, fieldNodeId, fieldControlId}` 形狀 | 301 |

### BRANCH 閘道器(1) + 分支項(2)

分支由兩層組成：**閘道器**（type 1，決定有哪些分支、求值順序、互斥還是並行）和**分支項**（type 2，每個分支自己的進入條件）。兩層都用同一個 `node save` 寫回，但讀法和鍵名各有坑，先看完再動手。

**坑 A — 閘道器設定讀不出，要從 `node list` 取。** `node get --type 1` 對閘道器回傳的 `flowIds` / `gatewayType` 全是 `null`（閘道器不是「詳情節點」）。閘道器的真實設定只在 `node list` 的 `flowNodeMap` 裡：

```bash
hap --json workflow node list <pid> | jq '.flowNodeMap["<gatewayId>"] | {flowIds, gatewayType}'
```

| 閘道器鍵 | 含義 | 值形態 |
|---|---|---|
| `flowIds` | 各分支項 ID 的**求值順序**陣列 | ② 分支項 ID 字串陣列 |
| `gatewayType` | 求值方式 | ① 1=並行（所有滿足條件的分支都進）；2=排他（按 `flowIds` 順序逐個判，命中第一個就停） |

寫回閘道器（只傳要改的鍵，走 `--type 1`）：

```bash
hap workflow node save <pid> <gatewayId> --type 1 -c '{"flowIds":["b3","b1","b2"],"gatewayType":2}'
```

**坑 B — 分支項條件「讀鍵 ≠ 寫鍵」，寫錯會靜默丟棄。** 這是分支裡最大的坑：

- **讀**：`node get --type 2` 把條件放在 `conditions` 欄位裡回傳（不是 `operateCondition`！`jq .operateCondition` 會得到 `null`）。
- **寫**：`node save --type 2` 的**規範寫鍵是 `operateCondition`**。值的二維陣列結構兩邊完全相同（外層 OR、內層 AND，→ [OperateCondition](../scripts/types/operate-condition.schema.json)）。
- 本 CLI 已對分支項（type 2）做相容：`-c` 裡用 `conditions` 也會自動對映成 `operateCondition`，所以**直接把讀到的 `{conditions}` 原樣寫回也能生效**。但請優先用 `operateCondition` 作規範鍵。

讀分支項條件別整段列印——`node get --type 2` 會帶上整張表的欄位目錄（`flowNodeList`/`flowNodeAppDtos`），輸出可達上百 KB。只取要看的鍵：

```bash
hap --json workflow node get <pid> <branchItemId> --type 2 | jq '{name, conditions}'
```

save 設定只需 `{name, desc, operateCondition}`；`flowNodeList`/`flowNodeAppDtos` 是隻讀的欄位目錄，不必回傳。

| 分支項鍵 | 含義 | 值形態 |
|---|---|---|
| `operateCondition` | 該分支的進入條件組（寫鍵；讀時叫 `conditions`） | ③ → [OperateCondition](../scripts/types/operate-condition.schema.json) |
| `resultTypeId` | 只讀：系統結果分支標記（1=透過 2=否決 3=有資料 4=無資料），非 0 的分支項不可編輯、不要回傳修改 | ① int（只讀） |

**給已有閘道器加一條並列分支（標準四步）。** `node add --type 2 --after <gatewayId>` 建的新分支項總是**追加到 `flowIds` 末尾**，排在「預設分支」（空條件那條）之後。排他閘道器（`gatewayType=2`）按 `flowIds` 順序求值、**空 `operateCondition` 的分支項 = 預設兜底分支，必須排在最後**，所以新分支幾乎總要手動前移：

```bash
# 1. 建分支項（自動入閘道器 flowIds 末尾）
hap workflow node add <pid> --type 2 -n "高優先順序" --after <gatewayId>
# → 記下回傳的新分支項 ID，設為 <newId>

# 2. 回寫閘道器，調整 flowIds 順序（更具體的條件靠前、空條件預設分支放最後）
hap workflow node save <pid> <gatewayId> --type 1 -c '{"flowIds":["<newId>","<existingId>","<defaultId>"]}'

# 3. 寫新分支項的進入條件
hap workflow node save <pid> <newId> --type 2 -c '{"operateCondition":[[{"filedId":"<欄位id>","filedTypeId":6,"conditionId":"9","conditionValues":[{"value":"0"}]}]]}'
# ↑ node save -c 走的是儲存形態（filedId 二維陣列），不收統一篩選寫法

# 4. 在新分支項後接動作節點
hap workflow node add <pid> --type 6 -n "處理" --after <newId> -a 1 --app-id <worksheet_id>
```
