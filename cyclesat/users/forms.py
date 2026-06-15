"""Модуль форм приложения пользователей."""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from users.models import CustomUser


class RegisterForm(UserCreationForm):
    """Форма регистрации."""

    email = forms.EmailField(
        required=True,
        help_text='Обязательное поле. Введите действующий email.',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите email'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите имя'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите фамилию'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите телефон'
        })
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Введите адрес доставки'
        })
    )

    class Meta:
        """Метаданные."""

        model = CustomUser
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'password1',
            'password2',
            'phone',
            'address'
        )

    def save(self, commit=True):
        """Метод сохранения данных."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            # Сохраняем дополнительные поля
            user.phone = self.cleaned_data['phone']
            user.address = self.cleaned_data['address']
            user.save()
        return user


class LoginForm(AuthenticationForm):
    """Форма входа."""

    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )
