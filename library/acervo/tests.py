from datetime import datetime

from django.test import TestCase
from django.urls import reverse_lazy
from model_bakery import baker

from .models.book import Book
from .models.category import Category
from .models.stock import Stock

# Create your tests here.


class BookTest(TestCase):
    def setUp(self):
        self.book = Book(
            name='Test Book',
            author='Test Author',
            publisher='Test Publisher',
            year=2022,
        )
        self.book.save()

    def test_book_str(self):
        self.assertEqual(str(self.book), 'Test Book - Test Author')

    def test_created_at(self):
        self.assertIsInstance(self.book.created_at, datetime)

    def test_updated_at(self):
        self.assertIsInstance(self.book.updated_at, datetime)

    def test_book_publisher(self):
        self.assertEqual(self.book.publisher, 'Test Publisher')

    def test_book_year(self):
        self.assertEqual(self.book.year, 2022)


class StockTest(TestCase):
    def setUp(self):
        self.book = baker.make(Book, name='Test Book', author='Test Author')
        self.stock = Stock(
            book=self.book,
            quantity=10,
        )
        self.stock.save()

    def test_stock_str(self):
        self.assertEqual(str(self.stock), 'Test Book - Test Author - 10')


class FilterTest(TestCase):
    def setUp(self):
        self.category1 = baker.make(Category, name='Ficção')
        self.category2 = baker.make(Category, name='Tecnologia')

        self.book1 = baker.make(
            Book,
            name='Teste Django',
            author='William Vincent',
            publisher='Editora Tech',
            year=2020,
        )
        self.book1.categories.add(self.category2)

        self.book2 = baker.make(
            Book,
            name='Python',
            author='Luciano Ramalho',
            publisher='Novatec',
            year=2015,
        )
        self.book2.categories.add(self.category2)

        self.book3 = baker.make(
            Book,
            name='1984',
            author='George Orwell',
            publisher='Companhia das Letras',
            year=1949,
        )
        self.book3.categories.add(self.category1)

        self.url = reverse_lazy('acervo:books')

    def test_book_view_filter(self):
        book = baker.make(Book, name='Test Book', author='Test Author')
        baker.make(Book, name='Test Book 2', author='levi')
        url = reverse_lazy('acervo:books')
        url += f'?author={book.author}'
        response = self.client.get(url)
        self.assertEqual(response.context['books'].qs.count(), 1)

    def test_filter_by_name(self):
        response = self.client.get(self.url, {'name': 'Django'})
        self.assertEqual(response.context['books'].qs.count(), 1)
        self.assertIn(self.book1, response.context['books'].qs)

    def test_filter_by_publisher(self):
        response = self.client.get(self.url, {'publisher': 'Novatec'})
        self.assertEqual(response.context['books'].qs.count(), 1)
        self.assertIn(self.book2, response.context['books'].qs)

    def test_filter_by_year(self):
        response = self.client.get(self.url, {'year': 2020})
        self.assertEqual(response.context['books'].qs.count(), 1)
        self.assertIn(self.book1, response.context['books'].qs)

    def test_filters_returns_all_books(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context['books'].qs.count(), 3)
