# 場景：改造一條工作流的節點（改設定 / 換收件人 / 插節點）

目標：給「訂單審批流」的通知節點換收件人，並在審批透過後插入一個「更新訂單狀態」節點。

## 命令序列

```bash
# 0. 定位流程與節點
hap --json workflow list <appId>                  # 拿 process_id（注意是位置參數）
hap --json workflow node list <process_id>        # 拿各節點 node_id 與 typeId

# 1. 改收件人：先讀現狀，照形改寫
hap --json workflow node get <process_id> <notice_node_id> > node.json
# 編輯 node.json 裡的 accounts —— 結構見 WorkflowAccounts 型別：
#   固定使用者 = {"type":1, "roleId":"<accountId>"}   ← accountId 放 roleId！
#   應用角色 = {"type":2, "entityId":"<appId>", "roleId":"<roleId>"}
hap workflow node save <process_id> <notice_node_id> \
  --type 27 --config '{"accounts": [{"type":2,"entityId":"<appId>","roleId":"<roleId>"}]}'

# 2. 在審批節點之後插入「更新記錄」節點
#    --app-id 這裡傳的是目標工作表 id,且必須在建立時就給(事後補不上)
hap workflow node add <process_id> --type 6 --action-id 2 \
  --name "更新订单状态" --after <approval_node_id> --app-id <ws_id>

# 3. 設定新節點寫哪些欄位（FieldWrite 結構,$模板取觸發記錄的值）
hap workflow node save-action <process_id> <new_node_id> \
  --fields '[{"fieldId":"<statusCtrlId>","type":11,"fieldValue":"<optKeyDone>"}]'

# 4. 重新發布使改動生效
hap workflow publish <process_id>
```

## 給已有分支閘道器加一條並列分支

完整逐鍵說明與坑位見 [nodes.md](../nodes.md) 的「BRANCH 閘道器(1) + 分支項(2)」段，關鍵四步：

```bash
# 閘道器設定讀不出（node get --type 1 全 null）——從 node list 取 flowIds/gatewayType
hap --json workflow node list <process_id> | jq '.flowNodeMap["<gatewayId>"] | {flowIds, gatewayType}'

# 1. 建分支項（自動追加到閘道器 flowIds 末尾，即排在空條件預設分支之後）
hap workflow node add <process_id> --type 2 -n "高优先级" --after <gatewayId>   # 記下 <newId>
# 2. 回寫閘道器調整順序：具體條件靠前、空條件預設分支放最後（排他閘道器 gatewayType=2 按序求值）
hap workflow node save <process_id> <gatewayId> --type 1 -c '{"flowIds":["<newId>","<existingId>","<defaultId>"]}'
# 3. 寫新分支項條件（寫鍵是 operateCondition；node get 讀出來叫 conditions）
hap workflow node save <process_id> <newId> --type 2 -c '{"operateCondition":[[{"filedId":"<fid>","filedTypeId":6,"conditionId":"9","conditionValues":[{"value":"0"}]}]]}'
# 4. 分支項後接動作節點
hap workflow node add <process_id> --type 6 -n "处理" --after <newId> -a 1 --app-id <ws_id>
```

## 注意

- **收件人 type 語義反直覺**（type 1 的 accountId 放 `roleId`，type 2 的 `entityId` 是 appId），寫錯會顯示「已刪除」且釋出失敗——見 [WorkflowAccounts](../../scripts/types/workflow-accounts.schema.json)。
- 節點條件用 [OperateCondition](../../scripts/types/operate-condition.schema.json)，欄位鍵是 `filedId`（不是 fieldId）。
- **分支項條件讀寫鍵名不對稱**：`node get --type 2` 讀出來在 `conditions` 欄位，`node save --type 2` 規範寫鍵是 `operateCondition`（CLI 也相容 `conditions` 自動對映）。詳見 [nodes.md](../nodes.md) BRANCH 段。
- 改完任何節點都要 `workflow publish` 才生效；釋出失敗時 `hap --json workflow get <process_id>` 看校驗錯誤。
- 給已有閘道器**加並列分支**已支援（見上）；分支內中間插入單個節點 / 複雜拓撲重排仍不支援——重建該流程或在頁面端手工調整。
