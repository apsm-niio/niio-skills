# 統計圖（chart）— 改一張已有的圖

統計圖掛在**一張工作表**上，命令都在 `hap worksheet chart` 下。圖表規格本身（`xaxes` /
`yaxisList` / `filter` / reportType 取值表）以 **`hap guide chart`** 為準，它是隨 CLI 版本走的；
本篇只講「改已有的圖」在 app-editor 場景下必須知道的幾條。

```bash
hap worksheet chart list <worksheetId>                # 個人圖 + 共享圖，全都列
hap worksheet chart list <worksheetId> --owner-only   # 只看自己的個人圖
hap --json worksheet chart get <reportId> --app-id <worksheetId>
hap worksheet chart update <reportId> --app-id <worksheetId> --name "新名字" --report-type 1 \
  -j '{"yaxisList":[{"controlId":"<金额字段>","controlType":6,"normType":4}]}'
hap worksheet chart delete <reportId> ...
```

## 四條容易搞錯的

1. **`--app-id` 要的是工作表 ID，不是應用 ID。** niio 的圖表規格里 `appId` 指的就是工作表。
   真正的應用 ID 只在 `--owner-app-id` 上，且只有規格里帶 `filter.items` 時才需要。
2. **`update` 只傳要改的項。** 它先把這張圖當前設定讀出來再把你寫的蓋上去，所以沒提到的維度、
   數值、排序、樣式、時間範圍都原樣保留。`--app-id`、`--name`、`--report-type` 三項**每次都要帶**。
3. **預設時間篩選只在新建時注入。** 一張圖沒有 `filter` 塊也能儲存成功，但渲染時沒有東西給查詢
   定範圍，頁面就顯示「無法形成圖表 / 構成要素不存在或已刪除」——編輯介面正常，一儲存就空白。
   `chart create` 會自動補一個「全部時間」的預設範圍；**`chart update` 不補**（否則會覆蓋這張圖
   原本設好的時間範圍）。所以改圖時不要把 `filter` 整塊刪掉。
4. **`chart list` 不加選項就是全部**（個人的和共享的都列），`--owner-only` 才是只看自己的。
   `-k/--keyword` 是**在本次取回的結果裡按名稱過濾**，不是讓伺服器端去搜；配合 `--page-size` 用時
   它只在這一頁裡篩。圖掛在聚合表上時加 `--app-type 2`。

大改結構時仍然推薦讀-改-寫：`chart get` 匯出 → 編輯 → `chart update -f chart.json`。
`get` 回傳的 `controls` / `account` / `createdDate` 等多餘欄位可以原樣帶回，伺服器端會忽略。

把圖擺到自訂頁上（元件形狀、48 柵格、version 語義）見 [custom-pages.md](custom-pages.md)。
