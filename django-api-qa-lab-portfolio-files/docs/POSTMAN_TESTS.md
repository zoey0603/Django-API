# Postman 測試腳本與操作說明

這份文件整理 Day 8 價格區間 API 的驗證重點，供審查者理解測試方式。下方的**可重複使用版本**是在原本練習腳本基礎上整理，請自行在 Postman 再跑一次，不能把未執行的改寫版宣稱為已驗收。

## 1. 合法價格區間

**Method:** GET  
**URL:** `http://127.0.0.1:8001/api/products/price-range/?min_price=100&max_price=500`

在 Postman → Scripts → Post-response 設定：

```javascript
pm.test("Valid price range returns 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Price range, count and sorting are correct", function () {
    const data = pm.response.json();
    const expectedMin = Number(pm.request.url.query.get("min_price"));
    const expectedMax = Number(pm.request.url.query.get("max_price"));

    pm.expect(data.products).to.be.an("array");
    pm.expect(data.min_price).to.eql(expectedMin);
    pm.expect(data.max_price).to.eql(expectedMax);
    pm.expect(data.count).to.eql(data.products.length);

    for (const product of data.products) {
        pm.expect(product.price).to.be.at.least(expectedMin);
        pm.expect(product.price).to.be.below(expectedMax);
    }

    for (let i = 0; i < data.products.length - 1; i++) {
        const current = data.products[i];
        const next = data.products[i + 1];

        pm.expect(current.price).to.be.at.most(next.price);
        if (current.price === next.price) {
            pm.expect(current.id).to.be.below(next.id);
        }
    }
});
```

此版本會直接取得 Request 中的參數，因此可在**合法且參數不重複**的情境下使用於 `100~500` 或 `10~21`；不需要手動把每份腳本裡的 `100`、`500` 改掉。

> 以上是欄位、條件與排序驗證，不會檢查「是否漏掉本來應該出現的商品」。如需完整性驗證，必須搭配固定測試資料與明確的商品 ID 預期清單。

## 2. 非法價格區間

**Method:** GET  
**URL:** `http://127.0.0.1:8001/api/products/price-range/?min_price=10&max_price=0.5`

```javascript
pm.test("Invalid range returns 400", function () {
    pm.response.to.have.status(400);

    const data = pm.response.json();
    pm.expect(data.error).to.eql("Invalid price range");
});
```

合法測試與非法測試**分開驗證預期狀態**，避免 API 錯誤回傳 400 時，原本應該取得 200 的測試卻意外顯示 Passed。

## 3. 建議的證據截圖

將你自己的實際畫面截圖放到 `docs/screenshots/`，可考慮：

- `django-tests-ok.png`：終端機顯示 `Ran 6 tests ... OK`。
- `postman-valid-range.png`：合法區間 Response 與 Test Results。
- `postman-same-price.png`：同價排序 Response 與 Test Results。
- `postman-invalid-range.png`：HTTP 400 與錯誤訊息。

上方只是**建議檔名**，目前並未附帶圖片，也沒有宣稱任何截圖已完成。
