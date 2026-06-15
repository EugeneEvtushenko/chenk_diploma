"""Модуль регистрации приложения корзины в админ-панели."""

from django.contrib import admin

from cart.models import Order, OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Настройка отображения модели заказов в админ-панели."""

    list_display = (
        'order_number',
        'user',
        'total_amount',
        'status',
        'created_at'
    )
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'user__username', 'user__email')
    readonly_fields = ('created_at',)

    fieldsets = (
        (None, {
            'fields': ('user', 'order_number', 'total_amount')
        }),
        ('Статус и даты', {
            'fields': ('status', 'created_at')
        }),
        ('Контактная информация', {
            'fields': ('shipping_address', 'contact_phone')
        }),
    )

    def get_queryset(self, request):
        """Метод для выдачи выборки данных в админ-панели."""
        return super().get_queryset(request).select_related('user')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Настройка отображения модели заказанных товаров в админ-панели."""

    list_display = ('order', 'product_name', 'price', 'quantity', 'total_price')
    list_filter = ('price', 'quantity')
    search_fields = ('product_name', 'order__order_number')

    def get_queryset(self, request):
        """Метод для выдачи выборки данных в админ-панели."""
        return super().get_queryset(request).select_related('order')
