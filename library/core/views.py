import logging
from datetime import timedelta

from django.shortcuts import render
from django.utils import timezone
from django.views.generic import TemplateView

from library.acervo.models import Book

logger = logging.getLogger('library')


BOOK_RATING_THRESHOLD = 4

class HomeView(TemplateView):
    template_name = 'home.html'

    def get(self, request, *args, **kwargs):
        latest_books = Book.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        )[:5]
        top_rated_books = list(
            filter(
                lambda book: book.average_rating > BOOK_RATING_THRESHOLD,
                Book.objects.all(),
            )
        )[:5]
        logger.info('Visualizando página inicial')
        return render(
            request,
            self.template_name,
            {'latest_books': latest_books, 'top_rated_books': top_rated_books},
        )


class DashboardView(TemplateView):
    template_name = 'dashboard.html'


class ProfileView(TemplateView):
    template_name = 'profile.html'
