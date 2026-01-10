# payments/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path("item/<int:id>/", views.item_page, name="item"),
    path("buy/<int:id>/", views.buy_item, name="buy_item"),

    path("order/<int:id>/", views.order_page, name="order"),
    path("buy-order/<int:id>/", views.buy_order, name="buy_order"),

    path("success", views.success, name="success"),
    path("cancel", views.cancel, name="cancel"),
]
