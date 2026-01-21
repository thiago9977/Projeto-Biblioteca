import django_filters
from django import forms

from .models import Book
from .models.category import Category


class BookFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    author = django_filters.CharFilter(lookup_expr='icontains')
    publisher = django_filters.CharFilter(lookup_expr='icontains')
    categories = django_filters.ModelMultipleChoiceFilter(
        queryset=Category.objects.all(), widget=forms.CheckboxSelectMultiple
    )
    year = django_filters.NumberFilter()

    class Meta:
        model = Book
        fields = ['name', 'author', 'publisher', 'year', 'categories']
