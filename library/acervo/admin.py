from django.contrib import admin
from .models import Book
# Register your models here.


@admin.register(Book)
class LivroAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'publisher', 'year')
    list_filter = ('author', 'publisher', 'year')
    search_fields = ('name', 'author', 'publisher', 'year')
    