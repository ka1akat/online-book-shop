from django.urls import path

from . import views
from .order_tools_views import CancelOrderView

urlpatterns = [
    path("categories/", views.CategoryListView.as_view()),
    path("store-reviews/", views.store_reviews_view),
    path("reports/demand/", views.demand_report_view),
    path("reports/monthly-sales/", views.monthly_sales_report_view),
    path("addresses/", views.addresses_view),
    path("products/", views.ProductListView.as_view()),
    path("products/low-stock/", views.LowStockView.as_view()),
    path("products/top-rated/", views.top_rated_view),
    path("products/<str:pk>/", views.ProductDetailView.as_view()),
    path("products/<str:pk>/reviews/", views.product_reviews_view),
    path("products/<str:pk>/notify/", views.product_notify_view),
    path("products/<str:pk>/similar/", views.similar_products_view),
    path("preferences/", views.preferences_view),
    path("recommendations/", views.recommendations_view),
    path("orders/", views.create_order_view),
    path("my-orders/", views.my_orders_view),
    path("notifications/", views.notifications_view),
    path("notifications/read/", views.notifications_read_view),
    path("wishlist/", views.wishlist_view),
    path("wishlist/<str:pk>/", views.wishlist_item_view),
    path("orders/<uuid:code>/", views.OrderDetailView.as_view()),
    path("orders/<uuid:code>/pay/", views.pay_order_view),
    path("orders/<int:order_id>/cancel/", CancelOrderView.as_view()),
    path("orders/<uuid:code>/tickets/", views.order_tickets_view),
    path("my-tickets/", views.my_tickets_view),
    path("register/", views.register_view),
    path("support/", views.support_view),
    path("login/", views.login_view),
]
