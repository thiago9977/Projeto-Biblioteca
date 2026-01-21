from django.contrib import admin

from library.emprestimos.models.emprestimo import Emprestimo
from library.emprestimos.models.reserva import Reserva


@admin.register(Emprestimo)
class EmprestimoAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'start_date', 'end_date', 'date_returned', 'multa')
    list_filter = ('book', 'user', 'date_returned')
    search_fields = ('book__name', 'user__username')


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'created_at', 'ativa')
    list_filter = ('book', 'user', 'ativa')
    search_fields = ('book__name', 'user__username')
