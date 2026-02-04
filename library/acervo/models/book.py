from django.db import models
from django.utils.text import slugify

from library.acervo.models.category import Category
from library.core.models import AbstractBaseModel


class Book(AbstractBaseModel):
    name = models.CharField(max_length=100, verbose_name='nome')
    slug = models.SlugField(
        max_length=100, verbose_name='slug', default='slug', unique=True, blank=True
    )
    author = models.CharField(max_length=100, verbose_name='autor')
    publisher = models.CharField(max_length=100, verbose_name='editora')
    year = models.IntegerField(verbose_name='ano')
    photo = models.ImageField(upload_to='books/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    isbn = models.CharField(max_length=13, blank=True, null=True)
    pages = models.IntegerField(verbose_name='páginas', blank=True, null=True)
    language = models.CharField(
        max_length=50, verbose_name='idioma', blank=True, null=True
    )
    categories = models.ManyToManyField(
        Category, verbose_name='categorias', blank=True, related_name='books'
    )
    is_available = models.BooleanField(default=True)

    @property
    def average_rating(self):
        """Calcula a média das avaliações do livro usando lambda e filter"""
        valid_ratings = list(
            filter(lambda review: review.rating is not None, self.reviews.all())
        )

        if not valid_ratings:
            return 0

        total = sum(map(lambda review: review.rating, valid_ratings))
        return round(total / len(valid_ratings), 2)

    @property
    def total_reviews(self):
        """Retorna o total de avaliações do livro"""
        return self.reviews.count()

    @property
    def rating_distribution(self):
        """Retorna a distribuição de avaliações por estrelas"""
        reviews = self.reviews.all()

        distribution = {
            'rating_5': reviews.filter(rating=5).count(),
            'rating_4': reviews.filter(rating=4).count(),
            'rating_3': reviews.filter(rating=3).count(),
            'rating_2': reviews.filter(rating=2).count(),
            'rating_1': reviews.filter(rating=1).count(),
        }

        return distribution

    @property
    def emprestimos_ativos(self):
        return self.emprestimos.filter(date_returned__isnull=True)

    class Meta:
        verbose_name = 'Livro'
        verbose_name_plural = 'Livros'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} - {self.author}'
