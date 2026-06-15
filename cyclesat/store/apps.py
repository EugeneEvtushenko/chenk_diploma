"""Модуль конфигурации приложения магазина."""

from django.apps import AppConfig


class StoreConfig(AppConfig):
    """Класс конфигурации приложения магазина."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'
    verbose_name = 'Магазин'
