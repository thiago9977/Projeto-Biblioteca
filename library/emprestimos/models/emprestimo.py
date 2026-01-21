from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from library.acervo.models import Book
from library.emprestimos.models.reserva import Reserva
from library.usuarios.models import User


class Emprestimo(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='emprestimos')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    date_returned = models.DateField(null=True, blank=True)
    multa = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.book.name} emprestado para {self.user.username}'

    @property
    def esta_ativo(self):
        return self.date_returned is None

    @property
    def esta_atrasado(self):
        if self.esta_ativo and self.end_date:
            return timezone.now().date() > self.end_date
        return False

    @property
    def dias_ate_vencimento(self):
        if self.esta_ativo and self.end_date:
            dias = self.end_date - timezone.now().date()
            return dias.days
        return None

    @property
    def dias_atraso(self):
        if self.esta_atrasado:
            dias = timezone.now().date() - self.end_date
            return dias.days
        return None

    @property
    def multa_atual(self):
        if self.esta_atrasado:
            return self.dias_atraso * 1.00
        return 0

    def calculate_multa(self):
        if not self.date_returned:
            return 0

        atraso = (self.date_returned - self.end_date).days
        if atraso > 0:
            return atraso * 1.00
        return 0

    @property
    def pode_renovar(self):
        if not self.esta_ativo or not self.end_date:
            return False

        hoje = timezone.now().date()
        dias_restantes = (self.end_date - hoje).days

        if dias_restantes != 1:
            return False

        existe_reserva = Reserva.objects.filter(book=self.book, ativa=True).exists()

        return not existe_reserva

    def clean(self):
        if self.id is None and not self.book.is_available:
            raise ValidationError('Este livro não está disponível para empréstimo.')

    def save(self, *args, **kwargs):
        created = self.id is None
        super().save(*args, **kwargs)

        if created:
            self.end_date = self.start_date + timedelta(days=14)
            super().save(update_fields=['end_date'])

        if self.date_returned:
            self.multa = self.calculate_multa()
            self.book.is_available = True
            self.book.save()
            super().save(update_fields=['multa'])
