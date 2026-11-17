from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET
import json
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from .models import Product

PRODUCTS = [
    {"id": 1, "name": "Notebook", "price": 150},
    {"id": 2, "name": "Pen", "price": 30},
    {"id": 3, "name": "Bag", "price": 800}
]

@ensure_csrf_cookie
def home(request):
    return render(request, "api/index.html")


@require_GET
def product_list(request):
    products = list(
        Product.objects.order_by("id")
        .values("id", "name", "price")
    )

    return JsonResponse({"products": products})


@require_GET
def product_detail(request, product_id):
    product = (
        Product.objects
        .filter(id=product_id)
        .values("id", "name", "price")
        .first()
    )

    if product is None:
        return JsonResponse(
            {"error": "Product not found"},
            status=404
        )

    return JsonResponse(product)

    
@require_GET
def products_under_price(request):
    # R-02：limit 為必填
    raw_limit = request.GET.get("limit")

    # R-03：必須是大於或等於 0 的整數
    # 使用 isascii() 與 isdigit() 可擋掉 "-5"、"1.5"、"abc"、"" 以及全形數字等
    if raw_limit is None or not (raw_limit.isascii() and raw_limit.isdigit()):
        return JsonResponse({"error": "Invalid limit"}, status=400)

    limit = int(raw_limit)

    # R-04、R-05、R-06：ORM 查詢，price < limit，依價格、ID 升冪
    products = list(
        Product.objects
        .filter(price__lt=limit)
        .order_by("price", "id")
        .values("id", "name", "price")
    )

    # R-07、R-09：無結果時 count 為 0、products 為 []
    return JsonResponse({
        "limit": limit,
        "count": len(products),
        "products": products,
    })
    
MAX_PRICE = 1_000_000_000
MIN_PRICE = 0

def _parse_price(raw_val: str) -> int | None:
    """驗證並解析價格字串，不合法則回傳 None。"""
    if not (raw_val.isascii() and raw_val.isdigit()):
        return None
    
    # 去除前導零，避免超長字串在 int() 轉換時消耗過多資源或觸發 Python 限制
    normalized = raw_val.lstrip("0") or "0"
    if len(normalized) > 10:
        return None
        
    return int(normalized)


@require_GET
def products_price_range(request):
    # 1. 檢查 Query Parameters 鍵值與數量是否精確匹配
    if set(request.GET.keys()) != {"min_price", "max_price"}:
        return JsonResponse({"error": "Invalid price range"}, status=400)

    min_list = request.GET.getlist("min_price")
    max_list = request.GET.getlist("max_price")
    if len(min_list) != 1 or len(max_list) != 1:
        return JsonResponse({"error": "Invalid price range"}, status=400)

    # 2. 解析並驗證數字格式
    min_price = _parse_price(min_list[0])
    max_price = _parse_price(max_list[0])
    if min_price is None or max_price is None:
        return JsonResponse({"error": "Invalid price range"}, status=400)

    # 3. 驗證數值範圍邏輯
    if not (MIN_PRICE <= min_price < max_price <= MAX_PRICE):
        return JsonResponse({"error": "Invalid price range"}, status=400)

    # 4. 查詢資料庫
    products = list(
        Product.objects
        .filter(price__gte=min_price, price__lt=max_price)
        .order_by("price", "id")
        .values("id", "name", "price")
    )

    return JsonResponse({
        "min_price": min_price,
        "max_price": max_price,
        "count": len(products),
        "products": products,
    })

@require_POST
@csrf_protect
def order_preview(request):

    # 1. 確認使用 JSON
    if request.content_type != "application/json":
        return JsonResponse(
            {"error": "Content-Type must be application/json"},
            status=415
        )

    # 2. 解析 JSON
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {"error": "Invalid JSON"},
            status=400
        )

    # 3. 確認 JSON 是物件
    if not isinstance(data, dict):
        return JsonResponse(
            {"error": "JSON object required"},
            status=400
        )

    # 4. 只接受指定欄位
    expected = {"username", "product_id", "quantity"}

    if set(data.keys()) != expected:
        return JsonResponse(
            {"error": "Unexpected or missing fields"},
            status=400
        )

    username = data["username"]
    product_id = data["product_id"]
    quantity = data["quantity"]

    # 5. 驗證使用者名稱
    if (
        not isinstance(username, str)
        or not username.strip()
        or len(username.strip()) > 30
    ):
        return JsonResponse(
            {"error": "Invalid username"},
            status=400
        )

    # 6. 驗證商品 ID
    if type(product_id) is not int:
        return JsonResponse(
            {"error": "Invalid product_id"},
            status=400
        )

    # 7. 驗證數量
    if type(quantity) is not int or not 1 <= quantity <= 10:
        return JsonResponse(
            {"error": "Quantity must be 1-10"},
            status=400
        )

    # 8. 尋找商品
    product = Product.objects.filter(id=product_id).first()

    if product is None:
        return JsonResponse(
            {"error": "Product not found"},
            status=404
        )

    # 9. 後端計算總價
    total = product.price * quantity

    # 10. 回傳試算結果
    return JsonResponse({
        "status": "preview",
        "username": username.strip(),
        "product": {
            "id": product.id,
            "name": product.name,
            "unit_price": product.price
        },
        "quantity": quantity,
        "total": total
    }, status=200)