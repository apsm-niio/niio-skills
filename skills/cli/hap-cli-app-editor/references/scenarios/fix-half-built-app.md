# 場景：修復建到一半出錯的應用

目標：一個應用生成中途失敗（缺表、缺欄位、檢視名錯、角色沒建全），把它補齊到可用狀態。

## 總思路

先**盤點差異**（期望結構 vs 實際結構），再**按依賴順序補**：表 → 欄位 → 檢視 → 角色/權限 → 工作流 → 頁面。每補一層都驗證後再進下一層，避免在錯誤地基上繼續疊。

## 命令序列

```bash
# 1. 盤點現狀
hap app-editor inspect <appId>          # 一眼看出缺哪些表/檢視/角色/頁面
hap --json worksheet fields <ws_id>     # 逐表核對欄位是否齊

# 2. 補缺的表（單條命令）
hap worksheet create <appId> "退貨單" --section-id <section_id>

# 3. 補缺的欄位（edit-spec,可一份 spec 串多個 op,後面的能引用前面建的）
cat > fix-fields.edit.json <<'EOF'
{ "app": "<appId>", "ops": [
  { "type": "field.add", "worksheet": "退貨單",
    "field": { "name": "退貨原因", "type": "Text" } },
  { "type": "field.add", "worksheet": "退貨單",
    "field": { "name": "狀態", "type": "SingleSelect",
               "options": ["待處理", "已完成"] } } ] }
EOF
hap app-editor validate fix-fields.edit.json && hap app-editor apply fix-fields.edit.json

# 4. 修錯名的檢視 / 補檢視
hap worksheet view update <ws_id> <view_id> --name "正確的名字"
hap worksheet view create <ws_id> "按狀態" --view-type board --group-control <statusCtrlId>

# 5. 補角色與權限
hap app role list -a <appId>
hap app role create -a <appId> --name "處理員" --description "處理退貨" \
  --type 0 --permission-scope 20
hap app role add-member <role_id> --user-ids <accountId> -a <appId>

# 6. 工作流沒釋出的釋出掉
hap --json workflow list <appId>        # enabled=false 的逐個檢查
hap workflow publish <process_id>

# 7. 終檢
hap app-editor inspect <appId>          # 結構齊了
```

## 注意

- **順序就是依賴**：檢視引用欄位、權限引用表和頁面、工作流引用欄位——缺哪層先補哪層的上游。
- 半成品裡可能有「建了一半的髒元素」（空表、錯名檢視）：刪除是破壞性操作，逐個跟使用者確認後再 `--yes` / `confirm:true`。
- 釋出工作流失敗，多半是節點裡引用了當時不存在的欄位/收件人——按 [workflow-node-rework.md](workflow-node-rework.md) 讀出節點照形修。
