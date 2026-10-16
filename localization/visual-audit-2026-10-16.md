# 素材視覺複查（2026-10-16）

基準版本：fb8e9fd4169d4ff7626aba27b749eb913d6b14a7。檢查範圍為 assets/sample-images 的 126 張素材及 sample_images.json 引用。

## 方法與結果

- 126 張以 6 張聯絡表逐一總覽；原圖 SHA256 全部符合既有 catalog。
- 放大檢查 asset-015、proof-012、screenshot-001、product-015、product-012、product-013 共 6 張。
- 本次可辨識範圍未發現上游平台名稱；細小標籤、螢幕內文與模糊背景不作「全部無殘留」保證。
- asset-015 的付款畫面含簡體字、可掃描 QR code，且原標籤為「標籤」，與圖意不符。保留原檔及來源紀錄，以 enabled=false 排除生成清單；未解碼或存取 QR code。
- 發現多處內容與關鍵字不符，修正 34 筆，避免 AI 依錯誤標籤選圖。無合適圖片時應留空或取得適當素材。
- screenshot-001 是通用數據畫面照片，不能宣稱 niio 截圖；proof 類為情境示意，不得作為真實交付或驗收證據。已加入 Step 6 指引。
- 未重製或改動任何圖片位元組，未執行 niio 遠端寫入，也未要求重跑先前驗收。

## 更新的關鍵字

| 檔案 | 依畫面更新的關鍵字 |
|---|---|
| product-001.jpg | 電腦工作桌 |
| product-002.jpg | 白色紙張紋理 |
| product-004.jpg | 烤箱 |
| product-006.jpg | 造型甜點 |
| product-007.jpg | 米飯料理 |
| product-008.jpg | 墨西哥夾餅 |
| product-009.jpg | 蒸籠點心 |
| product-010.jpg | 設備組裝 |
| product-011.jpg | 工程製圖 |
| product-012.jpg | CAD 設計畫面示意 |
| product-013.jpg | 平板設計畫面示意 |
| product-014.jpg | 星空風景 |
| product-020.jpg | 客廳 |
| product-021.jpg | 掃地機器人 |
| product-022.jpg | 烤箱 |
| product-023.jpg | 洗衣機 |
| product-024.jpg | 報紙與字謎 |
| product-032.jpg | 度假泳池 |
| product-049.jpg | 桌上型電腦 |
| product-051.jpg | 電腦與平板 |
| product-052.jpg | 智慧手錶 |
| product-053.jpg | 電子配件 |
| product-055.jpg | 彩色鉛筆 |
| product-063.jpg | 設備組裝 |
| asset-011.jpg | 打字機 |
| asset-014.jpg | 伺服器機櫃 |
| proof-010.jpg | 平板操作示意 |
| proof-011.jpg | 程式開發示意 |
| proof-012.jpg | 刷卡收銀設備 |
| issue-003.jpg | 物流路線地圖示意 |
| issue-005.jpg | 服務機器人 |
| marketing-001.jpg | 通用儀表板照片 |
| marketing-002.jpg | 介面設計討論 |
| screenshot-001.jpg | 通用數據儀表板示意（非 niio 畫面） |

## 驗證與待辦

生成後共有 125 個啟用圖片引用，均指向此儲存庫且檔案存在；停用素材不會被生成。38 項 Python 測試通過，含新增素材引用／雜湊／關鍵字核對。本地化生成 85 檔，未處理問題 0。

V01 素材複查已完成；實際生成畫面、外掛及 CLI 登入／終端畫面尚未檢查。保留英文書名、一般設備與商品標籤不等於上游平台品牌；若要求所有第三方商品品牌皆移除，需另定範圍。素材授權沿用既有紀錄，本次沒有重新作權利審查。
