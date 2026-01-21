from django.urls import path

from . import views

app_name = 'emprestimos'

urlpatterns = [
    path('book/<slug:slug>/reservar/', views.reserve_book, name='reserve_book'),
    path(
        'book/<slug:book_slug>/emprestar/', views.emprestar_book, name='emprestar_book'
    ),
    path('book/<int:emprestimo_id>/', views.renew_book, name='renew_book'),
]
