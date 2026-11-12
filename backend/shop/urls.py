from django.urls import path

from . import views

urlpatterns = [
    path("categories/", views.CategoryListView.as_view()),
    path("addresses/", views.addresses_view),
    path("products/", views.ProductListView.as_view()),
    path("products/low-stock/", views.LowStockView.as_view()),
    path("orders/", views.create_order_view),
    path("orders/<int:pk>/", views.OrderDetailView.as_view()),
    path("orders/<int:pk>/pay/", views.pay_order_view),
    path("register/", views.register_view),
    path("login/", views.login_view),
]
