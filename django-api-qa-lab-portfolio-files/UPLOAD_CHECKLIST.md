# 上傳 GitHub 前的檢查清單（請在本機操作）

此壓縮檔包含**作品集文件與設定範本**，不包含你的完整 Django 程式。請將 README.md、requirements.txt、.gitignore、docs/ 放進**原本有 manage.py 的專案根目錄**，並保留自己最新的 shop_demo/、api/、templates/、migrations/。不要把舊的 `tests.py` 附件覆蓋你最新的測試檔案。

## A. 先確認最新程式碼

- [ ] `api/tests.py` 已將 `test_very_large_number` 預期改成 HTTP 400，並驗證錯誤訊息。
- [ ] `test_price_sorting` 已建立同價測試資料，驗證 `(price, id)` 排序。
- [ ] `python manage.py test api -v 2` 再次顯示 `Ran 6 tests ... OK`。
- [ ] `api/views.py` 的 `products_price_range()` 已使用 `getlist()`、獨立解析數字，拒絕非法與重複參數。
- [ ] `api/urls.py` 已包含本作品展示的 API 路由。
- [ ] `requirements.txt` 的 Django 版本與實際本機環境相容。
- [ ] `db.sqlite3`、.env、Token、密碼與其他機密檔案不會被提交。

## B. 建議的 GitHub 方式

若此資料夾**還不是 Git 儲存庫**，可先於 GitHub 網站建立空白的公開 repo：`django-api-qa-lab`（不要勾選自動新增 README、.gitignore、License）。

PowerShell（請先進入含有 manage.py 的本機資料夾）：

```powershell
cd "C:\Projects\api-lab"
git status
```

若顯示 `fatal: not a git repository`，表示尚未初始化，再執行：

```powershell
git init
git branch -M main
```

接著檢查忽略規則和欲提交檔案：

```powershell
git status
git add .
git status
```

特別確認沒有 `db.sqlite3`、`.env`、`venv` / `.venv` 被加入。

```powershell
git commit -m "feat: add Django product API and QA test portfolio"
git remote -v
```

如果沒有任何 remote，再將 `YOUR_GITHUB_USERNAME` 替換成自己的 GitHub 帳號：

```powershell
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/django-api-qa-lab.git
git push -u origin main
```

如果 `origin` 已存在，不要重複執行 `git remote add`。先查看 `git remote -v` 指向何處，確認是你打算上傳的新專案；必要時使用 `git remote set-url origin <正確網址>`，避免誤推到既有的優惠券測試儲存庫。

## C. 上傳後驗證

- [ ] GitHub 首頁正常顯示 README，連結能打開詳細測試報告。
- [ ] 點進 `api/views.py`、`api/tests.py`，確定與本機最終版本一致。
- [ ] `requirements.txt`、`api/migrations/`、HTML 模板和 URL 設定都已上傳。
- [ ] 可以按 README 從乾淨環境啟動並執行測試。
- [ ] 手動測試案例數、Django 測試數和截圖證據沒有混用或誇大。
