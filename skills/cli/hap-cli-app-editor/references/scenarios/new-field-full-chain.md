# 場景：新增一個欄位，並讓它在檢視裡可見、對角色可用

目標：在「訂單」表加一個「優先順序」單選欄位，讓它出現在看板檢視的卡片上，且「銷售」角色能編輯它。

## 命令序列

```bash
# 0. 拿 id：工作表 / 视图 / 角色都从 inspect 里找
hap app-editor inspect <appId>
# 记下：订单表 ws_id、看板视图 view_id、销售角色 role_id

# 1. 加字段（edit-spec，增量安全路径）
cat > add-priority.edit.json <<'EOF'
{ "app": "<appId>", "ops": [
  { "type": "field.add", "worksheet": "订单",
    "field": { "name": "优先级", "type": "SingleSelect",
               "options": ["高", "中", "低"] } } ] }
EOF
hap app-editor validate add-priority.edit.json
hap app-editor apply add-priority.edit.json

# 2. 拿新字段的 controlId（后续步骤都用它）
hap --json worksheet fields <ws_id> | grep -A2 优先级

# 3. 让字段出现在看板卡片上（displayControls 是顶层视图属性）
hap --json worksheet view info <ws_id> <view_id>     # 先读现状
hap worksheet view update <ws_id> <view_id> \
  --view-json '{"displayControls": ["<已有controlId...>", "<新controlId>"]}' \
  --edit-attrs displayControls

# 4. 角色字段权限：默认新字段继承角色的工作表权限；
#    若角色用了字段级权限，需重新下发该表的权限条目
hap --json app role permissions <appId> <role_id>    # 先读现状判断
```

## 注意

- 第 3 步 `displayControls` 是**整組替換**，必須先讀出現有清單再追加,不能只傳新欄位。
- 第 1 步不要用 `hap worksheet update-fields` 加欄位——那是整表替換路徑。
- 驗證：`hap --json worksheet view info <ws_id> <view_id>` 確認 displayControls 包含新 controlId。
