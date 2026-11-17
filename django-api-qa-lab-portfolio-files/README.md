# Django 商品 API × QA 自動化測試

> **作品定位：Junior QA / API Testing / Junior Backend 學習專案**  
> 使用 Django + SQLite 開發商品查詢與訂單試算 API，並以 Postman、Django TestCase 驗證資料與錯誤處理。  
> 這是**個人練習與作品集專案**，不是商業正式系統，也沒有宣稱正式營運或部署。


| 項目 | 成果 |
| --- | --- |
| 後端功能 | **5 個 API 端點**：商品列表、商品明細、單一價格上限篩選、價格區間篩選、訂單試算 |
| 資料庫 | **SQLite + Django ORM**，透過 Model / Migration 建立及查詢商品資料 |
| API 驗證 | **Postman**：正常、無效輸入、HTTP 狀態碼、價格邊界、排序與回應欄位 |
| Django 自動化 | **6 項 TestCase**；最近一次本機執行結果：`Ran 6 tests ... OK`（2026-11-17） |
| 測試情境 | Day 7 價格區間 API **17 項手動測試情境**，回報的狀態碼與預期一致 |
| 前端整合 | HTML + JavaScript `fetch()` 顯示商品資料與訂單試算結果 |
| 版本管理 | Git（commit、branch、pull request、merge、restore、revert） |

**技術棧：** Python · Django · SQLite · Django ORM · SQL · Postman · JavaScript · HTML · Git

**詳細證據：** [API 測試報告](docs/TEST_REPORT.md) · [Postman 測試腳本與使用說明](docs/POSTMAN_TESTS.md)

## 專案功能與 API

| Method | Endpoint | 功能 | 常見狀態碼 |
| --- | --- | --- | --- |
| GET | `/api/products/` | 查詢商品列表 | `200` |
| GET | `/api/products/<id>/` | 查詢單一商品 | `200`、`404` |
| GET | `/api/products/under-price/?limit=500` | 查詢價格嚴格小於 `limit` 的商品 | `200`、`400`、`405` |
| GET | `/api/products/price-range/?min_price=100&max_price=500` | 查詢 `min_price <= price < max_price` 的商品 | `200`、`400`、`405` |
| POST | `/api/orders/preview/` | 驗證 JSON 並試算訂單金額，**不建立實際訂單** | `200`、`400`、`403`、`404`、`405`、`415` |

### 價格區間 API 範例

```http
GET /api/products/price-range/?min_price=100&max_price=500
```

```json
{
  "min_price": 100,
  "max_price": 500,
  "count": 2,
  "products": [
    {"id": 1, "name": "Notebook", "price": 150},
    {"id": 5, "name": "Mouse", "price": 450}
  ]
}
```

以上回應是**以測試時的商品資料為例**，不是每個全新資料庫都會有相同 ID 與商品。

### 訂單試算 API 範例

```http
POST /api/orders/preview/
Content-Type: application/json
```

```json
{
  "username": "tester01",
  "product_id": 2,
  "quantity": 2
}
```

```json
{
  "status": "preview",
  "username": "tester01",
  "product": {"id": 2, "name": "Pen", "unit_price": 30},
  "quantity": 2,
  "total": 60
}
```

**設計重點：** 商品單價由後端資料庫取得，不信任客戶端提交的價格；驗證使用者名稱、商品 ID、數量與 JSON 格式；保留 Django CSRF 防護。使用 Postman 發送 POST 時需先取得並附上有效 CSRF Cookie / Token。

## QA：我驗證了什麼？

- **正常與異常路徑：** 有效價格區間回傳 `200`；無效或缺少參數回傳 `400`；錯誤 HTTP Method 回傳 `405`。
- **邊界值：** 範圍下限包含、上限排除；`0`、合法最大值、超過最大值、極長數字。
- **資料品質：** `count === products.length`，商品價格必須符合過濾範圍。
- **排序：** 按價格升冪；相同價格時按商品 ID 升冪。額外建立同價商品驗證規則。
- **Bug 修正與迴歸：** 修正重複 Query Parameter、超長數字防護；發現並修正測試程式本身的錯誤斷言。

> **重要區別：** `Ran 6 tests ... OK` 是**六個指定測試通過**，不是 100% 測試覆蓋率；Day 7 的 17 項是手動 API 測試情境，不等同 17 支 Django 自動化測試。

## 如何在本機執行

**環境：** Windows / PowerShell；建議 Python 3.11+，實際套件版本以本專案 `requirements.txt` 為準。

```powershell
# 1. 取得專案（將 YOUR_GITHUB_USERNAME 替換成自己的帳號）
git clone https://github.com/YOUR_GITHUB_USERNAME/django-api-qa-lab.git
cd django-api-qa-lab

# 2. 建立虛擬環境
py -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. 安裝相依套件
python -m pip install -r requirements.txt

# 4. 建立 SQLite 資料表
python manage.py migrate

# 5. 啟動本機 Django
python manage.py runserver 127.0.0.1:8001
```

在瀏覽器開啟 `http://127.0.0.1:8001/`，或用 Postman 測試 API。**新建資料庫預設沒有教學用商品資料**，可使用 Django Shell 建立測試商品；Django 自動化測試則會自行建立隔離的測試資料。

### 執行自動化測試

```powershell
python manage.py test api -v 2
```

2026-11-17 本機驗收紀錄：

```text
Ran 6 tests in 0.024s
OK
```

## 建議的專案結構

```text
django-api-qa-lab/
├── README.md
├── requirements.txt
├── .gitignore
├── manage.py                 # 原 Django 專案程式
├── shop_demo/                # Django 專案設定
├── api/
│   ├── models.py             # Product Model
│   ├── views.py              # API 邏輯
│   ├── urls.py               # API Routes
│   ├── tests.py              # Django TestCase
│   ├── migrations/           # 需要提交 Migration 檔案
│   └── templates/api/        # HTML / JavaScript 示範頁面
└── docs/
    ├── TEST_REPORT.md
    └── POSTMAN_TESTS.md
```

這是**建議呈現結構**，必須搭配你真正已寫好的 Django 原始碼；本作品集文件不會自動建立這些 Python 檔案。

## 開發與學習過程

這個專案來自分階段的學習實作：先使用 Postman 測試 GET / POST，再建立 Django API、SQLite Model、ORM 查詢，最後補上價格區間驗證與 Django TestCase。過程中參考教學、IDE / AI 輔助，並親自操作測試、修正問題與核對結果。

**我能在面試時說明的重點：** HTTP 狀態碼與測試 PASS 的差別、`price__gte` 與 `price__lt`、同價排序、JSON 資料驗證、CSRF、Django ORM、測試預期錯誤造成的誤判，以及 Git 版本管理。

## 目前範圍與後續改善

- 此專案的訂單功能是**試算**，沒有真正寫入訂單，也尚未完成 CRUD。
- 尚未加入正式的登入／授權、分頁、正式部署與 CI。
- 單一價格上限 API（`under-price`）和價格區間 API 的極端輸入驗證尚未完全統一，後續可共用解析函式並補測。
- 作品集會持續補上實際 Postman 執行截圖、完整迴歸測試與 CRUD 練習。

---

**其他 QA 作品：** [優惠券手動測試與缺陷報告](https://github.com/zoey0603/qa-coupon-testing)
