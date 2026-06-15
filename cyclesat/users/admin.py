"""Модуль регистрации приложения пользователей в админ-панели."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Настройка отображения модели пользователей в админ-панели."""

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff'
    )
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительные данные', {
            'fields': (
                'phone',
                'address',
                'avatar'
            )
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительные данные', {
            'fields': (
                'phone',
                'address',
                'avatar'
            )
        }),
    )
