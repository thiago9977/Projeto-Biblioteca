import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from library.acervo.filter import BookFilter
from library.acervo.forms import BookReviewForm
from library.acervo.models import Book, Category
from library.emprestimos.models.emprestimo import Emprestimo
from library.emprestimos.models.reserva import Reserva
from library.emprestimos.models.historico import Historico

logger = logging.getLogger('library')


def book_detail(request, book_slug):
    book = get_object_or_404(Book, slug=book_slug)
    logger.info('Visualizando detalhes do livro: %s', book.name)
    reviews = book.reviews.select_related('user').order_by('-created_at')

    user_review = None
    emprestimo_usuario = None

    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()

        emprestimo_usuario = book.emprestimos.filter(
            user=request.user, date_returned__isnull=True
        ).first()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('usuarios:login')

        form = BookReviewForm(request.POST, instance=user_review)

        if form.is_valid():
            new_review = form.save(commit=False)
            new_review.book = book
            new_review.user = request.user
            new_review.save()

            return redirect('acervo:book_detail', book_slug=book.slug)
    else:
        form = BookReviewForm(instance=user_review)

    context = {
        'book': book,
        'reviews': reviews,
        'form': form,
        'user_review': user_review,
        'emprestimo_usuario': emprestimo_usuario,
    }
    return render(request, 'book_detail.html', context)


def books(request):
    logger.info('Visualizando lista de livros')
    books = BookFilter(request.GET, queryset=Book.objects.all())
    return render(request, 'books.html', {'books': books})


@login_required
def return_book(request, emprestimo_id):
    """Devolver livro"""
    if request.method == 'POST':
        emprestimo = get_object_or_404(Emprestimo, id=emprestimo_id, user=request.user)
        historico = Historico.objects.filter(book=emprestimo.book, user=emprestimo.user).last()

        if not emprestimo.esta_ativo:
            logger.error('Empréstimo não está ativo: %s', emprestimo.book.name)
            messages.error(request, 'Este empréstimo não está ativo.')
            return redirect('acervo:book_detail', book_slug=emprestimo.book.slug)

        if emprestimo.esta_atrasado:
            logger.warning('Livro devolvido com atraso: %s', emprestimo.book.name)
            messages.warning(
                request,
                f'Livro devolvido com {emprestimo.dias_atraso} dia(s) de atraso. '
                f'Multa: R$ {emprestimo.multa_atual}',
            )
        else:
            logger.info('Livro devolvido com sucesso: %s', emprestimo.book.name)
            messages.success(request, 'Livro devolvido com sucesso!')

        emprestimo.date_returned = timezone.now().date()
        emprestimo.save()

        if historico:
            historico.date_end = timezone.now().date()
            historico.save()

        book = emprestimo.book

        prox_reserva = (
            Reserva.objects.filter(book=emprestimo.book, ativa=True)
            .order_by('created_at')
            .first()
        )

        if prox_reserva:
            Emprestimo.objects.create(
                book=emprestimo.book,
                user=prox_reserva.user,
                start_date=timezone.now().date(),
                date_returned=None,
            )
            Historico.objects.create(
                book=emprestimo.book,
                user=prox_reserva.user,
                date_start=timezone.now().date(),
                date_end=None,
            )
            prox_reserva.ativa = False
            prox_reserva.save()
            book.is_available = False
            book.save()
            logger.info('Livro reservado com sucesso: %s', emprestimo.book.name)
            messages.success(request, 'Livro reservado com sucesso!')
        else:
            book.is_available = True
            book.save()
        return redirect('acervo:book_detail', book_slug=emprestimo.book.slug)

    return redirect('acervo:book_detail', book_slug=emprestimo.book.slug)


def categories(request):
    logger.info('Visualizando lista de categorias')
    categories = Category.objects.annotate(total_livros=Count('books'))
    return render(request, 'categorias.html', {'categories': categories})
