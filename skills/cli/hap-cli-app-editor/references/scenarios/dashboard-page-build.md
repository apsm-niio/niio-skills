# 場景：給已有應用搭一個看板頁（圖表 + 內嵌檢視 + 公告）

目標：新建「經營看板」自訂頁面，放一張按狀態統計的餅圖、一個訂單列表內嵌檢視和一段公告。

## 命令序列

```bash
# 0. 拿 id
hap app-editor inspect <appId>          # 拿分组 section_id、订单表 ws_id
hap --json worksheet view list <ws_id>  # 拿要内嵌的视图 view_id

# 1. 建页面壳子
hap custom-page create <appId> "经营看板" --section-id <section_id>
# 返回里记下 page_id

# 2. 先建图表（图表是独立对象,页面组件只引用它）
hap worksheet chart create <ws_id> --name "订单状态分布" \
  --report-type 3 --app-id <appId> \
  --spec-json '{"xaxes":[{"controlId":"<statusCtrlId>"}],
                "yaxisList":[{"controlId":"record_count","normType":5}]}'
# 返回里记下 reportId

# 3. 组件用 edit-spec 放上去（页面布局是整体读改写,不要手拼 components 数组）
cat > dashboard.edit.json <<'EOF'
{ "app": "<appId>", "ops": [
  { "type": "component.add", "page": "经营看板",
    "component": { "name": "订单状态分布", "type": "chart",
                   "value": "<reportId>", "worksheet": "<ws_id>" } },
  { "type": "component.add", "page": "经营看板",
    "component": { "name": "订单列表", "type": "view",
                   "worksheet": "<ws_id>", "view": "<view_id>" } },
  { "type": "component.add", "page": "经营看板",
    "component": { "name": "公告", "type": "richText",
                   "value": "<p>每周一更新</p>" } } ] }
EOF
hap app-editor validate dashboard.edit.json
hap app-editor plan dashboard.edit.json
hap app-editor apply dashboard.edit.json

# 4. 验证
hap --json custom-page info <page_id>
```

## 注意

- 圖表的 spec 結構（xaxes/yaxisList/筛选）見 custom-pages 與圖表字典；篩選條件用 [FilterCondition](../../scripts/types/filter-condition.schema.json)。
- 改已有圖表：`hap --json worksheet chart get <reportId> --app-id <ws_id>` 匯出 → 改 → `chart update` 回傳（注意 `--app-id` 是**工作表** id）。
- 元件欄位細節（佈局、元件型別表）見 [custom-pages.md](../custom-pages.md)。
