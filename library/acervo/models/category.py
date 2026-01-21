from django.db import models
from django.utils.text import slugify

from library.core.models import AbstractBaseModel


class Category(AbstractBaseModel):
    name = models.CharField(max_length=100, verbose_name='nome', unique=True)
    slug = models.SlugField(
        max_length=100, verbose_name='slug', default='slug', unique=True, blank=True
    )

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
