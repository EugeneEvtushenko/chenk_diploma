"""Модуль представлений для приложения пользователей."""

from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404

from store.models import Product, Category


def index(request):
    """Представление главной страницы со слайдером популярных товаров."""
    # Берём 6 последних добавленных товаров
    slider_products = Product.objects.all().order_by('-id')[:6]

    context = {
        'slider_products': slider_products,
    }
    return render(request, 'store/index.html', context)


def catalog(request):
    """Представление для страницы каталога."""
    # Получаем параметры
    search_query = request.GET.get('search', '').strip()
    category_id = request.GET.get('category', '')
    sort_by = request.GET.get('sort', 'name')
    sort_order = request.GET.get('order', 'asc')

    # Начальная выборка с загрузкой категорий
    products = Product.objects.select_related('category').all()

    # Фильтрация по категории
    if category_id:
        try:
            category_id = int(category_id)
            products = products.filter(category_id=category_id)
        except (ValueError, TypeError):
            pass

    # Поиск по названию товара, описанию и названию категории
    if search_query:
        search_lower = search_query.lower()
        filtered_products = []
        for product in products:
            # Проверяем название товара
            name_lower = product.name.lower()
            # Проверяем описание товара
            desc_lower = (product.description or '').lower()
            # Проверяем название категории
            category_name_lower = ''
            if product.category:
                category_name_lower = product.category.name.lower()

            # Если поисковый запрос есть в любом из полей — добавляем товар
            if (search_lower in name_lower or
                    search_lower in desc_lower or
                    search_lower in category_name_lower):

                filtered_products.append(product)

        products = filtered_products

    # Сортировка
    valid_sort_fields = ['name', 'price', 'production_year']
    if sort_by not in valid_sort_fields:
        sort_by = 'name'

    reverse = sort_order == 'desc'

    if isinstance(products, list):
        # Ручная сортировка для списка
        if sort_by == 'price':
            products.sort(
                key=lambda x: (x.price is None, x.price if x.price is not None else 0),
                reverse=reverse
            )
        elif sort_by == 'production_year':
            products.sort(
                key=lambda x: (x.production_year is None, x.production_year if x.production_year is not None else 0),
                reverse=reverse
            )
        else:  # sort_by == 'name'
            products.sort(
                key=lambda x: x.name.lower(),
                reverse=reverse
            )
    else:
        # Сортировка для QuerySet
        sort_field = f"-{sort_by}" if reverse else sort_by
        products = products.order_by(sort_field)

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Получаем все категории для отображения в фильтре
    categories = Category.objects.all().order_by('name')

    context = {
        'products': page_obj,
        'search_query': search_query,
        'category_id': category_id,
        'categories': categories,
        'sort_by': sort_by,
        'sort_order': sort_order,
        'paginator': paginator,
        'page_obj': page_obj,
    }

    return render(request, 'store/catalog.html', context)


def product_detail(request, product_id):
    """Страница с детальным описанием товара."""
    product = get_object_or_404(Product, id=product_id)

    context = {
        'product': product,
    }
    return render(request, 'store/product_details.html', context)
