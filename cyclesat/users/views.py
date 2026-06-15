"""Модуль представлений для приложения пользователей."""

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from users.forms import LoginForm, RegisterForm


def login_view(request):
    """Функция представления для логина."""
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')
                return redirect('users:profile')
            else:
                messages.error(request, 'Неверные учётные данные')
        else:
            messages.error(request, 'Ошибка в форме входа')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    """Функция представления для делогина."""
    logout(request)
    messages.info(request, 'Вы успешно вышли из системы')
    return redirect('store:index')


def register_view(request):
    """Функция представления для регистрации."""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешна! Добро пожаловать!')
            return redirect('store:catalog')
        else:
            messages.error(request, 'Исправьте ошибки в форме регистрации')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def user_profile(request):
    """Функция представления страницы профиля пользователя."""
    user = request.user

    context = {
        'user': user,
    }
    return render(request, 'users/profile.html', context)
