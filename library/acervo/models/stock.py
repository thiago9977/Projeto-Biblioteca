from django.db import models

from library.acervo.models.book import Book
from library.core.models import AbstractBaseModel


class Stock(AbstractBaseModel):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name='livro')
    quantity = models.PositiveIntegerField(verbose_name='quantidade', default=1)

    def __str__(self):
        return f'{self.book} - {self.quantity}'
