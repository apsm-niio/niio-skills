# 場景：給已有應用搭一個看板頁（圖表 + 內嵌檢視 + 公告）

目標：新建「經營看板」自訂頁面，放一張按狀態統計的餅圖、一個訂單清單內嵌檢視和一段公告。

## 命令序列

```bash
# 0. 拿 id
hap app-editor inspect <appId>          # 拿分組 section_id、訂單表 ws_id
hap --json worksheet view list <ws_id>  # 拿要內嵌的檢視 view_id

# 1. 建頁面殼子
hap custom-page create <appId> "經營看板" --section-id <section_id>
# 回傳裡記下 page_id

# 2. 先建圖表（圖表是獨立物件,頁面元件只引用它）
hap worksheet chart create <ws_id> --name "訂單狀態分佈" \
  --report-type 3 --app-id <appId> \
  --spec-json '{"xaxes":[{"controlId":"<statusCtrlId>"}],
                "yaxisList":[{"controlId":"record_count","normType":5}]}'
# 回傳裡記下 reportId

# 3. 元件用 edit-spec 放上去（頁面佈局是整體讀改寫,不要手拼 components 陣列）
cat > dashboard.edit.json <<'EOF'
{ "app": "<appId>", "ops": [
  { "type": "component.add", "page": "經營看板",
    "component": { "name": "訂單狀態分佈", "type": "chart",
                   "value": "<reportId>", "worksheet": "<ws_id>" } },
  { "type": "component.add", "page": "經營看板",
    "component": { "name": "訂單清單", "type": "view",
                   "worksheet": "<ws_id>", "view": "<view_id>" } },
  { "type": "component.add", "page": "經營看板",
    "component": { "name": "公告", "type": "richText",
                   "value": "<p>每週一更新</p>" } } ] }
EOF
hap app-editor validate dashboard.edit.json
hap app-editor plan dashboard.edit.json
hap app-editor apply dashboard.edit.json

# 4. 驗證
hap --json custom-page info <page_id>
```

## 注意

- 圖表的 spec 結構（xaxes/yaxisList/篩選）見 custom-pages 與圖表字典；篩選條件用 [FilterCondition](../../scripts/types/filter-condition.schema.json)。
- 改已有圖表：`hap --json worksheet chart get <reportId> --app-id <ws_id>` 匯出 → 改 → `chart update` 回傳（注意 `--app-id` 是**工作表** id）。
- 元件欄位細節（佈局、元件型別表）見 [custom-pages.md](../custom-pages.md)。
