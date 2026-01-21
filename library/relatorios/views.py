import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.shortcuts import render
from django.utils import timezone

from library.acervo.models import Book, Category
from library.emprestimos.models.emprestimo import Emprestimo
from library.usuarios.models import User

logger = logging.getLogger('library')


@staff_member_required
def dashboard_relatorios(request):
    logger.info('Acessando o relatório')

    total_livros = Book.objects.count()
    total_categorias = Category.objects.count()

    livros_disponiveis = Book.objects.filter(is_available=True).count()
    livros_emprestados = Book.objects.filter(is_available=False).count()

    livros_mais_emprestados = Book.objects.annotate(
        total_emprestimos=Count('emprestimos')
    ).order_by('-total_emprestimos')[:5]

    usuarios_mais_ativos = User.objects.annotate(
        total_emprestimos=Count('emprestimo')
    ).order_by('-total_emprestimos')[:5]

    hoje = timezone.now().date()
    emprestimos_hoje = Emprestimo.objects.filter(start_date=hoje).select_related(
        'book', 'user'
    )

    context = {
        'livros_top': livros_mais_emprestados,
        'usuarios_top': usuarios_mais_ativos,
        'emprestimos_hoje': emprestimos_hoje,
        'total_hoje': emprestimos_hoje.count(),
        'total_livros': total_livros,
        'total_categorias': total_categorias,
        'livros_disponiveis': livros_disponiveis,
        'livros_emprestados': livros_emprestados,
    }

    return render(request, 'painel_admin.html', context)
