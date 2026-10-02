# 場景：改造一條工作流的節點（改設定 / 換收件人 / 插節點）

目標：給「訂單審批流」的通知節點換收件人，並在審批透過後插入一個「更新訂單狀態」節點。

## 命令序列

```bash
# 0. 定位流程与节点
hap --json workflow list <appId>                  # 拿 process_id（注意是位置参数）
hap --json workflow node list <process_id>        # 拿各节点 node_id 与 typeId

# 1. 改收件人：先读现状，照形改写
hap --json workflow node get <process_id> <notice_node_id> > node.json
# 编辑 node.json 里的 accounts —— 结构见 WorkflowAccounts 类型：
#   固定用户 = {"type":1, "roleId":"<accountId>"}   ← accountId 放 roleId！
#   应用角色 = {"type":2, "entityId":"<appId>", "roleId":"<roleId>"}
hap workflow node save <process_id> <notice_node_id> \
  --type 27 --config '{"accounts": [{"type":2,"entityId":"<appId>","roleId":"<roleId>"}]}'

# 2. 在审批节点之后插入「更新记录」节点
#    --app-id 这里传的是目标工作表 id,且必须在创建时就给(事后补不上)
hap workflow node add <process_id> --type 6 --action-id 2 \
  --name "更新订单状态" --after <approval_node_id> --app-id <ws_id>

# 3. 配置新节点写哪些字段（FieldWrite 结构,$模板取触发记录的值）
hap workflow node save-action <process_id> <new_node_id> \
  --fields '[{"fieldId":"<statusCtrlId>","type":11,"fieldValue":"<optKeyDone>"}]'

# 4. 重新发布使改动生效
hap workflow publish <process_id>
```

## 給已有分支閘道器加一條並列分支

完整逐鍵說明與坑位見 [nodes.md](../nodes.md) 的「BRANCH 閘道器(1) + 分支項(2)」段，關鍵四步：

```bash
# 网关配置读不出（node get --type 1 全 null）——从 node list 取 flowIds/gatewayType
hap --json workflow node list <process_id> | jq '.flowNodeMap["<gatewayId>"] | {flowIds, gatewayType}'

# 1. 建分支项（自动追加到网关 flowIds 末尾，即排在空条件默认分支之后）
hap workflow node add <process_id> --type 2 -n "高优先级" --after <gatewayId>   # 记下 <newId>
# 2. 回写网关调整顺序：具体条件靠前、空条件默认分支放最后（排他网关 gatewayType=2 按序求值）
hap workflow node save <process_id> <gatewayId> --type 1 -c '{"flowIds":["<newId>","<existingId>","<defaultId>"]}'
# 3. 写新分支项条件（写键是 operateCondition；node get 读出来叫 conditions）
hap workflow node save <process_id> <newId> --type 2 -c '{"operateCondition":[[{"filedId":"<fid>","filedTypeId":6,"conditionId":"9","conditionValues":[{"value":"0"}]}]]}'
# 4. 分支项后接动作节点
hap workflow node add <process_id> --type 6 -n "处理" --after <newId> -a 1 --app-id <ws_id>
```

## 注意

- **收件人 type 語義反直覺**（type 1 的 accountId 放 `roleId`，type 2 的 `entityId` 是 appId），寫錯會顯示「已刪除」且釋出失敗——見 [WorkflowAccounts](../../scripts/types/workflow-accounts.schema.json)。
- 節點條件用 [OperateCondition](../../scripts/types/operate-condition.schema.json)，欄位鍵是 `filedId`（不是 fieldId）。
- **分支項條件讀寫鍵名不對稱**：`node get --type 2` 讀出來在 `conditions` 欄位，`node save --type 2` 規範寫鍵是 `operateCondition`（CLI 也相容 `conditions` 自動對映）。詳見 [nodes.md](../nodes.md) BRANCH 段。
- 改完任何節點都要 `workflow publish` 才生效；釋出失敗時 `hap --json workflow get <process_id>` 看校驗錯誤。
- 給已有閘道器**加並列分支**已支援（見上）；分支內中間插入單個節點 / 複雜拓撲重排仍不支援——重建該流程或在頁面端手工調整。
