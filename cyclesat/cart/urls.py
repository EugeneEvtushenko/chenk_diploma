"""Модуль маршрутизации приложения корзины."""

from django.urls import path

from cart import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/', views.add_to_cart, name='add_to_cart'),
    path('update-item/', views.update_cart_item, name='update_cart_item'),
    path('remove-item/', views.remove_from_cart, name='remove_from_cart'),
    path('create-order/', views.create_order, name='create_order'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
]
