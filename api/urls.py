from django.urls import path
from . import views

urlpatterns = [
    path("", views.home),
    path("api/products/", views.product_list),
    path("api/products/under-price/", views.products_under_price),   # 新增
    path("api/products/price-range/", views.products_price_range),   # 新增
    path("api/products/<int:product_id>/", views.product_detail),
    path("api/orders/preview/", views.order_preview),
]