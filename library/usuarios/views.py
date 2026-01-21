import logging

from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    get_user_model,
    update_session_auth_hash,
)
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import generic

from library.emprestimos.models.emprestimo import Emprestimo

from .forms import (
    CustomPasswordChangeForm,
    ProfileEditForm,
    SignInForm,
    SignUpForm,
)
from .models import Profile

logger = logging.getLogger('library')
User = get_user_model()


class RegisterView(generic.CreateView):
    form_class = SignUpForm
    template_name = 'register.html'
    success_url = reverse_lazy('usuarios:dashboard')

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('usuarios:profile')
        return render(request, self.template_name, {'form': self.form_class()})

    def form_valid(self, form):
        response = super().form_valid(form)
        auth_login(self.request, self.object)
        logger.info('Usuário registrado com sucesso')
        messages.success(
            self.request,
            f'Bem-vindo(a), {self.object.first_name}!'
            ' Sua conta foi criada com sucesso.',
        )
        return response


class LoginView(generic.FormView):
    form_class = SignInForm
    template_name = 'login.html'
    success_url = reverse_lazy('usuarios:profile')

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('usuarios:profile')
        return render(request, self.template_name, {'form': self.form_class()})

    def post(self, request):
        form = self.form_class(request.POST)
        if not form.is_valid():
            logger.error('Formulário inválido')
            messages.error(request, 'Usuário ou senha incorretos!')
            return render(request, self.template_name, {'form': form})

        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        remember = form.cleaned_data['remember']

        user = authenticate(username=username, password=password)
        if user:
            auth_login(request, user)
            messages.success(request, f'Bem-vindo(a), {user.first_name}!')

            if not remember:
                request.session.set_expiry(0)

            messages.success(request, 'Login realizado com sucesso!')
            logger.info('Login realizado com sucesso')
            return redirect('usuarios:profile')
        logger.error('Usuário ou senha incorretos')
        messages.error(request, 'Usuário ou senha incorretos!')
        return render(request, self.template_name, {'form': form})


class ProfileEditView(LoginRequiredMixin, generic.UpdateView):
    form_class = ProfileEditForm
    template_name = 'profile_edit.html'
    success_url = reverse_lazy('usuarios:profile')

    def get_object(self):
        return self.request.user.profile

    def form_valid(self, form):
        response = super().form_valid(form)
        logger.info('Perfil atualizado com sucesso')
        messages.success(self.request, 'Perfil atualizado com sucesso!')
        return response


class ChangePasswordView(LoginRequiredMixin, generic.FormView):
    form_class = CustomPasswordChangeForm
    template_name = 'change_password.html'
    success_url = reverse_lazy('usuarios:profile')

    def get_form_kwargs(self):
        """Passa o usuário para o form"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Executado quando o form é válido"""
        user = form.save()
        update_session_auth_hash(self.request, user)
        logger.info('Senha alterada com sucesso')
        messages.success(self.request, '✅ Senha alterada com sucesso!')
        return super().form_valid(form)

    def form_invalid(self, form):
        """Executado quando o form é inválido"""
        logger.error('Formulário inválido')
        messages.error(self.request, '❌ Por favor, corrija os erros abaixo.')
        return super().form_invalid(form)


def logout_view(request):
    """Logout de usuário"""
    auth_logout(request)
    logger.info('Logout realizado com sucesso')
    messages.info(request, 'Você saiu da sua conta.')
    return redirect('home')


@login_required
def dashboard(request):
    """Dashboard do usuário com dados reais"""
    logger.info('Visualizando dashboard')
    user = request.user

    active_reservations_data = (
        Emprestimo.objects.filter(user=user, date_returned__isnull=True)
        .select_related('book')
        .order_by('-start_date')
    )
    history_data = (
        Emprestimo.objects.filter(user=user)
        .select_related('book')
        .order_by('-start_date')
    )

    context = {
        'active_reservations': active_reservations_data,
        'active_reservations_count': len(active_reservations_data),
        'books_read_count': 0,
        'reviews_count': 0,
        'history': history_data,
        'has_history': history_data.exists(),
    }
    return render(request, 'dashboard.html', context)


@login_required
def profile(request):
    """Perfil do usuário"""
    logger.info('Visualizando perfil')
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)

    context = {
        'profile': profile,
    }
    return render(request, 'profile.html', context)


@login_required
def upload_avatar(request):
    """Upload de foto de perfil"""
    if request.method == 'POST' and request.FILES.get('avatar'):
        profile = request.user.profile
        profile.avatar = request.FILES['avatar']
        profile.save()
        logger.info('Foto de perfil atualizada com sucesso')
        messages.success(request, 'Foto de perfil atualizada com sucesso!')

    return redirect('usuarios:profile')


@login_required
def delete_account(request):
    """Exclui a conta do usuário"""
    logger.info('Excluindo conta')
    if request.method == 'POST':
        confirm_text = request.POST.get('confirm_delete')

        if confirm_text == 'EXCLUIR':
            user = request.user
            auth_logout(request)
            user.delete()
            logger.info('Conta excluída com sucesso')
            messages.success(request, 'Sua conta foi excluída permanentemente.')
            return redirect('home')
        else:
            logger.error('Texto de confirmação incorreto')
            messages.error(request, 'Texto de confirmação incorreto! Digite: EXCLUIR')

    return redirect('usuarios:profile')


@login_required
def update_preferences(request):
    logger.info('Atualizando preferências')
    if request.method == 'POST':
        messages.success(request, 'Preferências atualizadas com sucesso!')

    return redirect('usuarios:profile')


@login_required
def remove_avatar(request):
    if request.method == 'POST':
        profile = request.user.profile
        if profile.avatar:
            # Deletar o arquivo físico
            profile.avatar.delete(save=False)
            profile.avatar = None
            profile.save()
            logger.info('Foto de perfil removida com sucesso')
            messages.success(request, 'Foto de perfil removida com sucesso!')
        else:
            logger.info('Você não possui foto de perfil')
            messages.info(request, 'Você não possui foto de perfil.')

    return redirect('usuarios:profile')
