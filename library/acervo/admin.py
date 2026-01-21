from django.contrib import admin

from library.acervo.models import Book, BookReview, Category

# Register your models here.


@admin.register(Book)
class LivroAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'publisher', 'year', 'pages', 'is_available')
    list_filter = ('author', 'publisher', 'year', 'pages', 'language')
    search_fields = ('name', 'author', 'publisher', 'year')
    list_editable = ('is_available',)


@admin.register(Category)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(BookReview)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('book__name', 'user__username')
