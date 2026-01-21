from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from library.acervo.models import Book
from library.usuarios.models import User


class BookReview(models.Model):
    """Modelo para avaliações de livros"""

    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name='reviews', verbose_name='Livro'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='book_reviews',
        verbose_name='Usuário',
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Avaliação',
        help_text='Avaliação de 1 a 5 estrelas',
    )
    comment = models.TextField(blank=True, null=True, verbose_name='Comentário')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Data de criação')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Data de atualização')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'
        unique_together = ['book', 'user']

    def __str__(self):
        return f'{self.user.username} - {self.book.name} ({self.rating}★)'
