"""Модуль маршрутизации приложения корзины."""

from django.urls import path

from store import views

app_name = 'store'

urlpatterns = [

    path(
        '',
        views.index,
        name='index'
    ),

    path(
        'catalog/',
        views.catalog,
        name='catalog'
    ),

    path(
        'product/<int:product_id>/',
        views.product_detail,
        name='product_detail'
    ),
]
