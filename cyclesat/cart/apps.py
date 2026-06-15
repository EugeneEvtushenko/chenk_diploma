"""Модуль конфигурации приложения корзины."""

from django.apps import AppConfig


class CartConfig(AppConfig):
    """Класс конфигурации приложения корзины."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cart'
    verbose_name = 'Корзина'
