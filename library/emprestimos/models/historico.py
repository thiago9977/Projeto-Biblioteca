from datetime import datetime
from django.db import models
from library.acervo.models import Book
from library.usuarios.models import User
from .emprestimo import Emprestimo

class Historico(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    date_start = models.DateField(auto_now_add=True, verbose_name='data de emprestimo')
    date_end = models.DateField(null=True, blank=True, verbose_name='data de devolução')

    class Meta:
        ordering = ['-date_start']
        verbose_name = 'Historico'
        verbose_name_plural = 'Historicos'

    def __str__(self):
        return f'{self.book.name} emprestado para {self.user.username}'
