"""Модуль регистрации приложения магазина в админ-панели."""

from django.contrib import admin
from django.utils.html import mark_safe
from store.models import Product, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Настройка отображения модели категорий в админ-панели."""

    list_display = ('name', 'slug')
    search_fields = ('name',)


class IsInStockFilter(admin.SimpleListFilter):
    """Настройка метода определения наличия в админ-панели."""

    title = 'В наличии'
    parameter_name = 'in_stock'

    def lookups(self, request, model_admin):
        """Метод для кастомного фильтра админ-панели."""
        return (('1', 'Да'), ('0', 'Нет'))

    def queryset(self, request, queryset):
        """Кастомный фильтр админ-панели."""
        if self.value() == '1':
            return queryset.filter(amount__gt=0)
        elif self.value() == '0':
            return queryset.filter(amount=0)
        return queryset


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Настройка отображения модели Product в админ-панели Django."""

    list_display = (
        'name',
        'category',
        'formatted_price',
        'amount',
        'get_availability_display',
        'production_year',
        'is_in_stock',
    )

    list_filter = (
        'category',
        IsInStockFilter,
    )

    search_fields = (
        'name',
        'description',
        'category__name',
    )

    list_editable = (
        'amount',
    )

    fieldsets = (
        ('Основная информация', {
            'fields': (
                'name',
                'description',
                'category',
                'image',
                'image_preview'
            )
        }),
        ('Характеристики товара', {
            'fields': (
                'production_year',
                'price',
                'amount'
            ),
        }),
    )

    ordering = ('name',)
    list_per_page = 20
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        """Метод для превью изображений в админ-панели."""
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-width: 300px; max-height: 200px;" />')
        return 'Изображение не загружено'
    image_preview.short_description = 'Превью изображения'

    def has_module_permission(self, request):
        """Разрешает доступ к разделу товаров в админ-панели."""
        return request.user.is_active
