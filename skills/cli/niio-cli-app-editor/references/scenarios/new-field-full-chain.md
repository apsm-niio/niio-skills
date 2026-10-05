# 場景：新增一個欄位，並讓它在檢視裡可見、對角色可用

目標：在「訂單」表加一個「優先順序」單選欄位，讓它出現在看板檢視的卡片上，且「銷售」角色能編輯它。

## 命令序列

```bash
# 0. 拿 id：工作表 / 檢視 / 角色都從 inspect 裡找
hap app-editor inspect <appId>
# 記下：訂單表 ws_id、看板檢視 view_id、銷售角色 role_id

# 1. 加欄位（edit-spec，增量安全路徑）
cat > add-priority.edit.json <<'EOF'
{ "app": "<appId>", "ops": [
  { "type": "field.add", "worksheet": "訂單",
    "field": { "name": "優先順序", "type": "SingleSelect",
               "options": ["高", "中", "低"] } } ] }
EOF
hap app-editor validate add-priority.edit.json
hap app-editor apply add-priority.edit.json

# 2. 拿新欄位的 controlId（後續步驟都用它）
hap --json worksheet fields <ws_id> | grep -A2 優先順序

# 3. 讓欄位出現在看板卡片上（displayControls 是頂層檢視屬性）
hap --json worksheet view info <ws_id> <view_id>     # 先讀現狀
hap worksheet view update <ws_id> <view_id> \
  --view-json '{"displayControls": ["<已有controlId...>", "<新controlId>"]}' \
  --edit-attrs displayControls

# 4. 角色欄位權限：預設新欄位繼承角色的工作表權限；
#    若角色用了欄位級權限，需重新下發該表的權限條目
hap --json app role permissions <appId> <role_id>    # 先讀現狀判斷
```

## 注意

- 第 3 步 `displayControls` 是**整組替換**，必須先讀出現有清單再追加,不能只傳新欄位。
- 第 1 步不要用 `hap worksheet update-fields` 加欄位——那是整表替換路徑。
- 驗證：`hap --json worksheet view info <ws_id> <view_id>` 確認 displayControls 包含新 controlId。
