"""Модуль представлений для приложения пользователей."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models, transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.crypto import get_random_string
from django.views.decorators.http import require_POST

from cart.models import Cart, CartItem, Order, OrderItem
from store.models import Product


@login_required
def cart_detail(request):
    """Функция представления для просмотра корзины."""
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('product').all()
    total_price = cart.total_price

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'cart/cart_details.html', context)


@require_POST
@login_required
def add_to_cart(request):
    """Функция представления для добавления товара в корзину."""
    try:
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity', 1)

        if not product_id:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Не указан ID товара'
                }, json_dumps_params={'ensure_ascii': False})
            else:
                messages.error(request, 'Не указан ID товара')
                return redirect('store:catalog')

        try:
            quantity = int(quantity)
            if quantity < 1:
                quantity = 1
        except (ValueError, TypeError):
            quantity = 1

        cart, created = Cart.objects.get_or_create(user=request.user)

        # Явная обработка отсутствия товара
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Товар не найден'
                }, json_dumps_params={'ensure_ascii': False})
            else:
                messages.error(request, 'Товар не найден')
                return redirect('store:catalog')

        product_name = product.name
        price_at_addition = product.price

        # Создание или обновление CartItem с заполнением price_at_addition
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={
                'quantity': quantity,
                'price_at_addition': price_at_addition
            }
        )

        if not created:
            # Обновляем количество и цену
            cart_item.quantity += quantity
            cart_item.price_at_addition = price_at_addition
            cart_item.save()

        # Расчёт общего количества товаров
        updated_total_items = cart.items.aggregate(
            total=models.Sum('quantity')
        )['total'] or 0

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # AJAX
            return JsonResponse({
                'success': True,
                'message': f'{product_name} добавлен в корзину',
                'total_items': updated_total_items
            }, json_dumps_params={'ensure_ascii': False})
        else:  # Обычный POST
            messages.success(request, f'{product_name} добавлен в корзину')
            return redirect('cart:cart_detail')
    except Exception as e:
        print(f"Ошибка в add_to_cart: {e}")  # Для отладки
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': f'Ошибка сервера: {str(e)}'
            }, json_dumps_params={'ensure_ascii': False})
        else:
            messages.error(request, 'Ошибка при добавлении товара в корзину')
            return redirect('store:catalog')


@require_POST
@login_required
def update_cart_item(request):
    """Функция представления для редактирования корзины."""
    try:
        cart_item_id = request.POST.get('cart_item_id')
        new_quantity = request.POST.get('quantity')

        if not cart_item_id or not new_quantity:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Не указаны ID товара или количество'
                }, json_dumps_params={'ensure_ascii': False})
            else:
                messages.error(request, 'Не указаны ID товара или количество')
                return redirect('cart:cart_detail')

        try:
            new_quantity = int(new_quantity)
            if new_quantity < 1:
                raise ValueError
        except (ValueError, TypeError):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Количество должно быть положительным числом'
                }, json_dumps_params={'ensure_ascii': False})
            else:
                messages.error(
                    request, 'Количество должно быть положительным числом'
                )
                return redirect('cart:cart_detail')

        cart = Cart.objects.get(user=request.user)
        cart_item = get_object_or_404(CartItem, id=cart_item_id, cart=cart)
        product_name = cart_item.product.name

        # Обновляем количество
        cart_item.quantity = new_quantity
        cart_item.save()

        updated_total_items = sum(item.quantity for item in cart.items.all())
        updated_total_price = cart.get_total_price()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # AJAX
            return JsonResponse({
                'success': True,
                'message': f'Количество {product_name} обновлено',
                'total_items': updated_total_items,
                'total_price': updated_total_price,
                'item_total': cart_item.get_item_total()
            }, json_dumps_params={'ensure_ascii': False})
        else:  # Обычный POST
            messages.success(request, f'Количество {product_name} обновлено')
            return redirect('cart:cart_detail')
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, json_dumps_params={'ensure_ascii': False})
        else:
            messages.error(request, 'Ошибка при обновлении количества')
            return redirect('cart:cart_detail')


@require_POST
@login_required
def remove_from_cart(request):
    """Функция представления для удаления товаров из корзины."""
    try:
        cart_item_id = request.POST.get('cart_item_id')

        if not cart_item_id:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Не указан ID товара'
                }, json_dumps_params={'ensure_ascii': False})
            else:
                return redirect('cart:cart_detail')

        cart = Cart.objects.get(user=request.user)
        cart_item = get_object_or_404(CartItem, id=cart_item_id, cart=cart)
        product_name = cart_item.product.name
        cart_item.delete()

        updated_total_items = sum(item.quantity for item in cart.items.all())

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # AJAX
            return JsonResponse({
                'success': True,
                'message': f'{product_name} удалён из корзины',
                'total_items': updated_total_items
            }, json_dumps_params={'ensure_ascii': False})
        else:  # Обычный POST‑запрос
            messages.success(request, f'{product_name} удалён из корзины')
            return redirect('cart:cart_detail')
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, json_dumps_params={'ensure_ascii': False})
        else:
            messages.error(request, 'Ошибка при удалении товара из корзины')
            return redirect('cart:cart_detail')


@require_POST
@login_required
def create_order(request):
    """Функция представления для оформления заказа."""
    try:
        cart = get_object_or_404(Cart, user=request.user)
        cart_items = cart.items.select_related('product').all()

        if not cart_items:
            messages.error(request, 'Корзина пуста')
            return redirect('users:profile')

        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                order_number=get_random_string(length=10).upper(),
                total_amount=cart.total_price,
                shipping_address='Самовывоз',
                contact_phone='Не указан',
                status='pending'
            )

            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product_name=cart_item.product.name,
                    price=cart_item.price_at_addition,
                    quantity=cart_item.quantity,
                    total_price=cart_item.total_price
                )

        # Очищаем корзину
        cart.items.all().delete()

        # Добавляем сообщение для отображения на странице профиля
        messages.success(
            request, f'Заказ #{order.order_number} создан успешно!'
        )

        # Перенаправляем на страницу профиля
        return redirect('users:profile')
    except Exception as e:
        print(f"Ошибка при создании заказа: {e}")
        messages.error(request, f'Ошибка сервера: {str(e)}')
        return redirect('cart:detail')


@login_required
def order_detail(request, order_id):
    """Функция представления деталей заказа."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {'order': order}
    return render(request, 'cart/order_details.html', context)
