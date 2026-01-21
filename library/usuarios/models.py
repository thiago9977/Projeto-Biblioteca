from django.contrib.auth import get_user_model
from django.db import models

from library.core.models import AbstractBaseModel

User = get_user_model()


class Profile(AbstractBaseModel):
    user = models.OneToOneField(
        'auth.User', on_delete=models.CASCADE, related_name='profile'
    )
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    cep = models.CharField(max_length=10, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True)
    country = models.CharField(max_length=100, default='Brasil')

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        return f'Perfil de {self.user.username}'
