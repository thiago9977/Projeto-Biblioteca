import logging
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from library.acervo.models import Book
from library.emprestimos.models.emprestimo import Emprestimo
from library.emprestimos.models.reserva import Reserva
from library.emprestimos.models.historico import Historico

logger = logging.getLogger('library')


@login_required
def emprestar_book(request, book_slug):
    book = get_object_or_404(Book, slug=book_slug)
    user = request.user
    if not book.is_available:
        logger.error('Livro não disponível para empréstimo: %s', book.name)
        messages.error(request, 'Este livro não está disponível para empréstimo.')
        return redirect('acervo:book_detail', book_slug=book.slug)

    if Emprestimo.objects.filter(book=book, date_returned__isnull=True).exists():
        logger.error('Livro já emprestado: %s', book.name)
        messages.error(request, 'Este livro já foi emprestado.')
        return redirect('acervo:book_detail', book_slug=book.slug)

    Emprestimo.objects.create(book=book, user=user)
    Historico.objects.create(book=book, user=user)

    book.is_available = False
    book.save()
    logger.info('Livro emprestado: %s', book.name)
    messages.success(request, 'Livro emprestado com sucesso.')
    return redirect('acervo:book_detail', book_slug=book.slug)


@login_required
def history_view(request):
    logger.info(
        'Visualizando histórico de empréstimos do usuário: %s', request.user.username
    )
    history = (
        Emprestimo.objects.filter(user=request.user)
        .select_related('book')
        .order_by('-start_date')
    )
    return render(request, 'emprestimos/history.html', {'history': history})


@login_required
def reserve_book(request, slug):
    book = get_object_or_404(Book, slug=slug)
    user = request.user

    existe = Reserva.objects.filter(book=book, user=user, ativa=True).exists()
    if existe:
        logger.error('Livro já reservado: %s', book.name)
        messages.error(request, 'Você já reservou este livro.')
        return redirect('acervo:book_detail', book_slug=book.slug)

    Reserva.objects.create(book=book, user=user)
    logger.info(f'Livro reservado: {book.name}')
    messages.success(request, 'Livro reservado com sucesso.')
    return redirect('acervo:book_detail', book_slug=book.slug)


@login_required
def renew_book(request, emprestimo_id):
    emprestimo = get_object_or_404(Emprestimo, id=emprestimo_id, user=request.user)

    if request.method == 'POST':
        if not emprestimo.pode_renovar:
            logger.error('Empréstimo não pode ser renovado: %s', emprestimo.book.name)
            messages.error(request, 'Este empréstimo não pode ser renovado.')
            return redirect('acervo:book_detail', book_slug=emprestimo.book.slug)

        emprestimo.end_date = emprestimo.end_date + timedelta(days=7)
        emprestimo.save()

        logger.info('Empréstimo renovado: %s', emprestimo.book.name)
        messages.success(request, 'Empréstimo renovado por mais 7 dias!')
        return redirect('acervo:book_detail', book_slug=emprestimo.book.slug)

    return redirect('acervo:book_detail', book_slug=emprestimo.book.slug)
