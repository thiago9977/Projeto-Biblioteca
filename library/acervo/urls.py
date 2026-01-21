from django.urls import path

from . import views

app_name = 'acervo'

urlpatterns = [
    path('categories/', views.categories, name='categories'),
    path('<slug:book_slug>/', views.book_detail, name='book_detail'),
    path('', views.books, name='books'),
    path('return/<int:emprestimo_id>/', views.return_book, name='return_book'),
]
