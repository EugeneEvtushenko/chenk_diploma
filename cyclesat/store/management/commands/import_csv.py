"""Модуль для импорта данных из csv-файлов."""

import csv
import sys

from django.core.management import BaseCommand

from store.management.commands.validators_on_methods import ValidatorCSV
from store.models import Category, Product

DATA_DIR = 'static/data'


class Command(BaseCommand):
    """Импортирует данные из CSV-файлов в базу данных."""

    def handle(self, *args, **options):
        """Настройка импорта данных."""
        data_dir = DATA_DIR

        imported_data = {
            'категории': (self.import_category, 'category.csv'),
            'товары': (self.import_product, 'product.csv'),
        }

        for table, (function, file) in imported_data.items():
            self.stdout.write(self.style.NOTICE(f'Загружаем {table}:'))
            try:
                function(f'{data_dir}/{file}')
                self.stdout.write(self.style.SUCCESS(f'{table} загружены'))
            except (
                Exception
            ) as e:
                self.stdout.write(self.style.ERROR(f'{table} не загружены'))
                self.stdout.write(self.style.ERROR(f'{e}',))
                sys.exit(1)
        self.stdout.write(self.style.SUCCESS('\nВСЕ ДАННЫЕ УСПЕШНО ЗАГРУЖЕНЫ'))

    def read_import_file(self, filepath):
        """Функция чтения csv-файла."""
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)

    def import_category(self, filepath):
        """Имопрт категорий."""
        data = self.read_import_file(filepath)

        ValidatorCSV.not_empty_check(data)
        ValidatorCSV.integer_check(data, 'id')
        ValidatorCSV.unique_check(data, 'id', 'slug')
        ValidatorCSV.slug_check(data, 'slug',)

        for row in data:
            Category.objects.get_or_create(
                id=int(row['id']),
                name=row['name'],
                slug=row['slug']
            )

    def import_product(self, filepath):
        """Имопрт товаров."""
        data = self.read_import_file(filepath)

        ValidatorCSV.not_empty_check(data)
        ValidatorCSV.integer_check(data, 'id', 'production_year', 'category')
        ValidatorCSV.unique_check(data, 'id')
        ValidatorCSV.year_no_more_check(data, 'year')

        for row in data:
            Product.objects.get_or_create(
                id=int(row['id']),
                name=row['name'],
                description=row['description'],
                category=Category.objects.get(id=int(row['category'])),
                production_year=int(row['production_year']),
                price=row['price'],
                amount=int(row['amount']),
                image=row['image'],
            )
