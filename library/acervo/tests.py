from datetime import datetime
from django.test import TestCase
from .models import Book, Stock
from model_bakery import baker
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
    
class StockTest(TestCase):
    def setUp(self):
        self.book = baker.make(
            Book,
            name='Test Book',
            author='Test Author'
        )
        self.stock = Stock(
            book=self.book,
            quantity=10,
        )
        self.stock.save()

    def test_stock_str(self):
        self.assertEqual(str(self.stock), 'Test Book - Test Author - 10')