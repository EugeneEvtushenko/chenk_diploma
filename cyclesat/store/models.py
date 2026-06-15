"""Модуль моделей приложения магазина."""

from django.db import models


class Category(models.Model):
    """Модель для категорий товаров."""

    name = models.CharField(
        max_length=255,
        verbose_name='Название',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name="Слаг"
    )

    class Meta:
        """Метаданные."""

        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        """Представление модели."""
        return self.name


class Product(models.Model):
    """Модель товара для каталога магазина."""

    name = models.CharField(
        max_length=255,
        verbose_name='Название',
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True,
        null=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name="Категория"
    )

    production_year = models.PositiveIntegerField(
        verbose_name='Год производства',
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена',
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
    )
    image = models.ImageField(
        upload_to='products/',
        verbose_name='Изображение',
        blank=True,
        null=True,
    )

    class Meta:
        """Метаданные."""

        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['name']

    def __str__(self):
        """Представление модели."""
        return self.name

    def is_in_stock(self):
        """Проверяет, есть ли товар в наличии."""
        return self.amount > 0
    is_in_stock.boolean = True
    is_in_stock.short_description = 'В наличии'

    def formatted_price(self):
        """Возвращает цену с разделителем тысяч и символом валюты."""
        return f'{self.price:,.2f} ₽'.replace(',', ' ').replace('.', ',')
    formatted_price.short_description = 'Цена с ₽'

    def get_availability_display(self):
        """Возвращает текстовое представление наличия товара."""
        return "В наличии" if self.is_in_stock() else "Нет в наличии"
    get_availability_display.short_description = 'Наличие'
