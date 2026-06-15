"""Модуль моделей приложения корзины."""

from django.conf import settings
from django.db import models

from store.models import Product


class Cart(models.Model):
    """Модель корзины."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        """Представление модели."""
        return f'Корзина пользователя {self.user.username}'

    @property
    def total_price(self):
        """Метод построения списка корзины."""
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    """Модель товаров в корзине."""

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(
        default=1
    )
    price_at_addition = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    class Meta:
        """Метаданные."""

        unique_together = ('cart', 'product')

    def __str__(self):
        """Представление модели."""
        return f'{self.quantity} × {self.product.name}'

    @property
    def total_price(self):
        """Метод подсчета стоимости корзины."""
        return self.quantity * self.price_at_addition


class Order(models.Model):
    """Модель заказа."""

    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
        ('shipped', 'Отправлен'),
        ('completed', 'Завершён'),
        ('cancelled', 'Отменён'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    order_number = models.CharField(
        max_length=20,
        unique=True
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    shipping_address = models.TextField()
    contact_phone = models.CharField(
        max_length=15
    )

    class Meta:
        """Метаданные."""

        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        """Представление модели."""
        return f'Заказ #{self.order_number} от {self.user.username}'


class OrderItem(models.Model):
    """Модель товаров в заказе."""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product_name = models.CharField(
        max_length=255
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    class Meta:
        """Метаданные."""

        verbose_name = "Заказанные товары"
        verbose_name_plural = "Заказанные товары"

    def __str__(self):
        """Представление модели."""
        return f'{self.quantity} × {self.product_name}'
