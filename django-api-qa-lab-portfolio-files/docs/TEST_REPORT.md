# API 測試報告｜Django 商品查詢與價格區間

**測試對象：** 本機 Django + SQLite 練習專案（`http://127.0.0.1:8001`）  
**紀錄日期：** 2026-11-17  
**測試工具：** Postman、Django `TestCase`、Python / SQLite  
**性質：** 個人教學專案的功能驗證，不代表正式產品驗收。

## 1. 執行摘要

| 指標 | 已回報結果 | 說明 |
| --- | --- | --- |
| Django 自動測試 | **6 / 6 通過** | 本機輸出 `Ran 6 tests in 0.024s`、`OK` |
| Day 7 API 測試情境 | **17 項** | 逐筆對照預期與實際 HTTP 狀態碼；並提供部分 JSON 回應 |
| Day 8 Postman 成功驗證 | **已回報 Passed** | 合法區間與欄位、篩選、排序條件 |
| Day 8 Postman 失敗驗證 | **已回報 Passed** | 非法小數上限應回傳 `400` 與 `Invalid price range` |
| 測試覆蓋率 | **未測量** | 不把 6/6 誤稱為全面測試覆蓋 |

> 本報告依實際提交的操作紀錄彙整。正式放上 GitHub 前，請確認本機最新 `api/tests.py` 已包含你後續修正的測試，並重新執行一次驗收。

## 2. 價格區間 API 規格

**Endpoint：** `GET /api/products/price-range/`  
**參數：** `min_price`、`max_price`，均為必填、僅允許各一個值。  
**合法條件：** `0 <= min_price < max_price <= 1,000,000,000`；接受 ASCII 十進位整數及前導零。  
**篩選規則：** `min_price <= product.price < max_price`。  
**排序規則：** `price ASC, id ASC`。  
**成功回應：** HTTP 200，回傳 `min_price`、`max_price`、`count`、`products`。  
**參數不合法：** HTTP 400，`{"error":"Invalid price range"}`。  
**錯誤 Method：** HTTP 405。

## 3. Day 7 手動測試情境

| # | 情境 | 請求參數／操作 | 預期 HTTP | 回報的實際結果 |
| --- | --- | --- | --- | --- |
| 01 | 一般合法查詢 | `min_price=100&max_price=500` | 200 | 200，Notebook / Mouse，共 2 件 |
| 02 | 排除上限等值 | `min_price=100&max_price=450` | 200 | 200，不包含 Mouse |
| 03 | 包含下限等值 | `min_price=150&max_price=450` | 200 | 200，包含 Notebook、不含 Mouse |
| 04 | 無符合商品 | `min_price=700&max_price=750` | 200 | 200，`count=0`、`products=[]` |
| 05 | 相等零值 | `min_price=0&max_price=0` | 400 | 400 |
| 06 | 負數 | `min_price=-1&max_price=100` | 400 | 400 |
| 07 | 非數字字串 | `min_price=a&max_price=c` | 400 | 400 |
| 08 | 小數 | `min_price=500.5&max_price=750` | 400 | 400 |
| 09 | 布林文字 | `min_price=true&max_price=true` | 400 | 400 |
| 10 | 下限大於上限 | `min_price=500&max_price=150` | 400 | 400 |
| 11 | 同時缺少參數 | 未傳 `min_price`、`max_price` | 400 | 400 |
| 12 | 價格升冪 | `min_price=450&max_price=801` | 200 | 200，Mouse (450) → Bag (800) |
| 13 | 同價 ID 升冪 | `min_price=10&max_price=21` | 200 | 200，ruler (ID 4) → pencil (ID 6)，皆 20 元 |
| 14 | 合法範圍上下限 | `min_price=0&max_price=1000000000` | 200 | 200，共 6 件 |
| 15 | 超出最大上限 | `min_price=0&max_price=1000000001` | 400 | 400 |
| 16 | 上下限相等 | `min_price=150&max_price=150` | 400 | 400 |
| 17 | 不允許的方法 | POST 至價格區間 API | 405 | 405 |

**測試資料說明：** 部分測試使用 SQLite 中新增的 `Mouse` (450)、`ruler` (20)、`pencil` (20)；由於開發資料庫可能改變，實際商品 ID 與回應筆數應以測試當下資料為準。

**需區分的概念：** 第 16 項是「上下限數值相等」，**不是**「同名 Query Parameter 重複出現」。重複參數屬於 Day 8 程式與自動測試補強的範圍。

## 4. Django 自動化測試

檔案：`api/tests.py`；以 Django `TestCase` 的測試資料庫隔離執行。

| TestCase | 驗證目標 |
| --- | --- |
| `test_valid_price_range` | 合法區間回傳 HTTP 200、商品筆數正確 |
| `test_missing_parameters` | 缺少必要參數回傳 HTTP 400 與正確錯誤訊息 |
| `test_duplicate_parameter` | 同名 Query Parameter 重複出現應被拒絕 |
| `test_equal_price_boundary` | 商品價格剛好等於上限時不應包含 |
| `test_price_sorting` | 價格升冪；同價依 ID 升冪（最終版加入同價測試資料） |
| `test_very_large_number` | 極長數字回傳 HTTP 400 而不是未處理錯誤 |

最新本機輸出（依 2026-11-17 回報）：

```text
Ran 6 tests in 0.024s
OK
```

執行指令：

```powershell
python manage.py test api -v 2
```

## 5. Postman 自動驗證

測試重點：

- 合法範圍回傳 `200`，`count` 與 `products.length` 一致。
- 每件商品滿足 `min_price <= price < max_price`。
- 商品依價格升冪，同價時依 ID 升冪。
- 非法輸入回傳 `400`，`error` 等於 `Invalid price range`。

使用的測試程式與注意事項請見 [POSTMAN_TESTS.md](POSTMAN_TESTS.md)。不同測試案例應有各自明確的預期狀態碼，避免將 200／400 混在一個分支式測試中，導致錯誤回應也能通過。

## 6. 發現與修正紀錄

| 問題 | 影響 | 修正及驗證方向 |
| --- | --- | --- |
| 使用 `get()` 讀取重複參數 | 同名參數可能只取得最後一筆 | 改為 `getlist()` 並要求每個參數剛好一筆 |
| 將兩個價格字串連在一起檢查長度 | 合法的大數區間可能被錯誤拒絕 | 分別正規化、檢查位數後再轉整數 |
| 對數千位原始數字直接使用 `int()` | 可能產生未處理的例外 | 先驗證數字型態及有效位數，再轉換 |
| Postman 同時要求價格與 ID 全域嚴格遞增 | 對同價商品或 ID 不連續排序誤判 | 先比較價格；只有價格相等時才比較 ID |
| Django TestCase 把非法超長數字預期設為 `200` | 測試預期與規格不一致 | 修正預期為 `400` 並驗證錯誤 JSON |

## 7. 測試限制與後續事項

- 目前沒有量測程式碼覆蓋率，也沒有正式的 CI Pipeline。
- 手動測試和自動測試的數量不同，不能直接相加成自動化案例數。
- 舊版 `under-price` 端點的極端輸入驗證尚可與 `price-range` 統一。
- 訂單試算沒有寫入訂單紀錄；真正的 CRUD、資料完整性與交易驗證預計於下一階段新增。
- 建議補上實際的 Postman Test Results、Django 測試終端畫面截圖；本報告未將不存在的圖檔當成證據。
