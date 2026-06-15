"""Модуль моделей приложения пользователей."""

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Расширенная модель пользователей."""

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Телефон"
    )
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name="Адрес"
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name="Аватар"
    )

    class Meta:
        """Метаданные."""

        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        """Представление модели."""
        return self.username
