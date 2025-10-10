from django.db import models
from library.core.models import AbstractBaseModel

# Create your models here.


class Book(AbstractBaseModel):
    name = models.CharField(max_length=100, verbose_name='nome')
    author = models.CharField(max_length=100, verbose_name='autor')
    publisher = models.CharField(max_length=100, verbose_name='editora')
    year = models.IntegerField(verbose_name='ano')

    def __str__(self):
        return f'{self.name} - {self.author}'

class Stock(AbstractBaseModel):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name='livro')
    quantity = models.PositiveIntegerField(verbose_name='quantidade', default=1)

    def __str__(self):
        return f'{self.book} - {self.quantity}'
    
    