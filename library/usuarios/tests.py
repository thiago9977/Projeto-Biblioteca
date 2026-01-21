from django.contrib import auth

# Create your tests here.
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .models import Profile


class ProfileTests(TestCase):
    """Testes para visualização e edição de perfil"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@email.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
        )
        Profile.objects.create(user=self.user)

    def test_profile_page_requires_login(self):
        """Testa se página de perfil requer login"""
        response = self.client.get(reverse('usuarios:profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_profile_page_loads_when_logged_in(self):
        """Testa se página de perfil carrega quando logado"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('usuarios:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        self.assertIn('profile', response.context)

    def test_profile_created_automatically(self):
        """Testa se o perfil é criado automaticamente"""
        self.user = User.objects.create_user(
            username='testuser1', password='testpass123'
        )
        Profile.objects.create(user=self.user)
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, Profile)

    def test_update_profile_basic_info(self):
        self.user = User.objects.create_user(
            username='testuser2', password='testpass123'
        )
        Profile.objects.create(user=self.user)
        """Testa atualização de informações básicas"""
        self.client.login(username='testuser2', password='testpass123')

        response = self.client.post(
            reverse('usuarios:profile_edit'),
            {
                'first_name': 'Updated',
                'last_name': 'Name',
                'email': 'updated@email.com',
                'phone': '11999999999',
                'bio': 'Updated bio',
                'cep': '12345-678',
                'address': 'Updated Street, 123',
                'city': 'São Paulo',
                'state': 'SP',
            },
        )

        self.assertEqual(response.status_code, 302)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')
        self.assertEqual(self.user.email, 'updated@email.com')

        profile = self.user.profile
        profile.refresh_from_db()
        self.assertEqual(profile.phone, '11999999999')
        self.assertEqual(profile.bio, 'Updated bio')
        self.assertEqual(profile.cep, '12345-678')
        self.assertEqual(profile.address, 'Updated Street, 123')
        self.assertEqual(profile.city, 'São Paulo')
        self.assertEqual(profile.state, 'SP')

    def test_update_profile_with_birth_date(self):
        """Testa atualização com data de nascimento"""
        self.client.login(username='testuser', password='testpass123')

        response = self.client.post(
            reverse('usuarios:profile_edit'),
            {
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'test@email.com',
                'birth_date': '1990-01-15',
            },
        )

        self.assertEqual(response.status_code, 302)

        profile = self.user.profile
        profile.refresh_from_db()
        self.assertEqual(str(profile.birth_date), '1990-01-15')

    def test_update_profile_without_birth_date(self):
        """Testa atualização sem data de nascimento (campo opcional)"""
        self.user = User.objects.create_user(
            username='testuser3', password='testpass123'
        )
        Profile.objects.create(user=self.user)
        self.client.login(username='testuser3', password='testpass123')

        response = self.client.post(
            reverse('usuarios:profile_edit'),
            {
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'test@email.com',
                'birth_date': '',
            },
        )

        self.assertEqual(response.status_code, 302)

        profile = self.user.profile
        profile.refresh_from_db()
        self.assertIsNone(profile.birth_date)


class PasswordChangeTests(TestCase):
    """Testes para mudança de senha"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='oldpass123')
        self.client.login(username='testuser', password='oldpass123')

    def test_change_password_success(self):
        """Testa mudança de senha com sucesso"""
        response = self.client.post(
            reverse('usuarios:change_password'),
            {
                'old_password': 'oldpass123',
                'new_password1': 'newpass123',
                'new_password2': 'newpass123',
            },
        )

        self.assertEqual(response.status_code, 302)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass123'))
        self.assertFalse(self.user.check_password('oldpass123'))

        response = self.client.get(reverse('usuarios:profile'))
        self.assertEqual(response.status_code, 200)

    def test_change_password_wrong_current(self):
        """Testa mudança com senha atual incorreta"""
        response = self.client.post(
            reverse('usuarios:change_password'),
            {
                'old_password': 'wrongpass',
                'new_password1': 'newpass123',
                'new_password2': 'newpass123',
            },
        )

        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('oldpass123'))

    def test_change_password_mismatch(self):
        """Testa mudança com confirmação diferente"""
        response = self.client.post(
            reverse('usuarios:change_password'),
            {
                'old_password': 'oldpass123',
                'new_password1': 'newpass123',
                'new_password2': 'differentpass',
            },
        )

        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('oldpass123'))

    def test_change_password_too_short(self):
        """Testa mudança com senha muito curta"""
        response = self.client.post(
            reverse('usuarios:change_password'),
            {
                'old_password': 'oldpass123',
                'new_password1': 'short',
                'new_password2': 'short',
            },
        )

        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('oldpass123'))


class DeleteAccountTests(TestCase):
    """Testes para exclusão de conta"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_delete_account_success(self):
        """Testa exclusão de conta com confirmação correta"""
        user_id = self.user.id

        response = self.client.post(
            reverse('usuarios:delete_account'), {'confirm_delete': 'EXCLUIR'}
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

        self.assertFalse(User.objects.filter(id=user_id).exists())

        self.assertFalse(Profile.objects.filter(user_id=user_id).exists())

        response = self.client.get(reverse('usuarios:profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_delete_account_wrong_confirmation(self):
        """Testa exclusão com confirmação incorreta"""
        user_id = self.user.id

        response = self.client.post(
            reverse('usuarios:delete_account'), {'confirm_delete': 'wrong'}
        )

        self.assertEqual(response.status_code, 302)

        self.assertTrue(User.objects.filter(id=user_id).exists())

    def test_delete_account_case_sensitive(self):
        """Testa se a confirmação é case-sensitive"""
        user_id = self.user.id

        response = self.client.post(
            reverse('usuarios:delete_account'), {'confirm_delete': 'excluir'}
        )

        self.assertEqual(response.status_code, 302)

        self.assertTrue(User.objects.filter(id=user_id).exists())


class AuthViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='usuario_teste',
            email='teste@example.com',
            password='senha12345',
            first_name='Teste',
            last_name='User',
        )

    def test_register_get(self):
        """Deve renderizar o template de registro ao acessar via GET"""
        response = self.client.get(reverse('usuarios:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_register_post_campos_obrigatorios(self):
        """Deve exibir erro se campos obrigatórios não forem preenchidos"""
        response = self.client.post(
            reverse('usuarios:register'),
            {
                'username': '',
                'email': '',
                'password1': '',
                'password2': '',
                'first_name': '',
                'last_name': '',
            },
        )
        self.assertEqual(response.status_code, 200)

        form = response.context['form']
        required_fields = [
            'username',
            'email',
            'password1',
            'password2',
            'first_name',
            'last_name',
        ]
        for field in required_fields:
            self.assertIn(
                field,
                form.errors,
                f"O campo '{field}' deveria ter erro de obrigatório.",
            )

        self.assertTrue(
            form.errors, 'O formulário deveria conter erros de campos obrigatórios.'
        )

    def test_register_post_senhas_diferentes(self):
        """Deve exibir erro se as senhas não coincidirem"""
        response = self.client.post(
            reverse('usuarios:register'),
            {
                'username': 'novo',
                'email': 'novo@example.com',
                'password1': 'senha12345',
                'password2': 'outra12345',
                'first_name': 'Novo',
                'last_name': 'User',
            },
        )
        self.assertEqual(response.status_code, 200)

        # Verifica se o erro 'As senhas não coincidem' aparece no form
        form = response.context['form']
        self.assertTrue(
            any(
                'As senhas não coincidem' in e for e in form.errors.get('password2', [])
            ),
            f'Erros encontrados: {form.errors.as_data()}',
        )

    def test_register_post_sucesso(self):
        """Deve criar um novo usuário e redirecionar para o dashboard"""
        response = self.client.post(
            reverse('usuarios:register'),
            {
                'username': 'novo_user',
                'email': 'novo@example.com',
                'password1': 'senha12345',
                'password2': 'senha12345',
                'first_name': 'Novo',
                'last_name': 'Usuário',
            },
        )
        self.assertRedirects(response, reverse('usuarios:dashboard'))
        self.assertTrue(User.objects.filter(username='novo_user').exists())

    def test_register_usuario_logado_redireciona(self):
        """Usuário autenticado não deve acessar a página de registro"""
        self.client.login(username='usuario_teste', password='senha12345')
        response = self.client.get(reverse('usuarios:register'))
        self.assertRedirects(response, reverse('usuarios:profile'))

    def test_login_get(self):
        """Deve renderizar o template de login"""
        response = self.client.get(reverse('usuarios:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_post_incorreto(self):
        """Deve exibir erro se credenciais forem inválidas"""
        response = self.client.post(
            reverse('usuarios:login'),
            {'username': 'usuario_teste', 'password': 'errado'},
        )
        messages = list(response.context['messages'])
        self.assertTrue(any('Usuário ou senha incorretos' in str(m) for m in messages))

    def test_login_post_correto(self):
        """Deve autenticar e redirecionar para o profile"""
        response = self.client.post(
            reverse('usuarios:login'),
            {'username': 'usuario_teste', 'password': 'senha12345'},
        )
        self.assertRedirects(response, reverse('usuarios:profile'))
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_login_usuario_ja_autenticado(self):
        """Usuário logado que acessa /login deve ser redirecionado"""
        self.client.login(username='usuario_teste', password='senha12345')
        response = self.client.get(reverse('usuarios:login'))
        self.assertRedirects(response, reverse('usuarios:profile'))

    def test_logout_view(self):
        """Deve fazer logout e redirecionar para home"""
        self.client.login(username='usuario_teste', password='senha12345')
        response = self.client.get(reverse('usuarios:logout'))
        self.assertRedirects(response, reverse('home'))
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)
