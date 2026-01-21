from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction

from library.usuarios.models import Profile

User = get_user_model()


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    phone = forms.CharField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email já está cadastrado!')
        return email

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if phone:
            phone = phone.replace('-', '').replace('(', '').replace(')', '')
        return phone

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('As senhas não coincidem.')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            with transaction.atomic():
                user.save()
                Profile.objects.create(user=user, phone=self.cleaned_data['phone'])

        return user


class SignInForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    remember = forms.BooleanField(required=False)


class ProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(required=False)
    birth_date = forms.DateField(required=False)
    bio = forms.CharField(required=False)
    cep = forms.CharField(required=False)
    address = forms.CharField(required=False)
    city = forms.CharField(required=False)
    state = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].initial = self.instance.user.first_name
        self.fields['last_name'].initial = self.instance.user.last_name
        self.fields['email'].initial = self.instance.user.email
        self.fields['phone'].initial = self.instance.phone
        self.fields['birth_date'].initial = self.instance.birth_date
        self.fields['bio'].initial = self.instance.bio
        self.fields['cep'].initial = self.instance.cep
        self.fields['address'].initial = self.instance.address
        self.fields['city'].initial = self.instance.city
        self.fields['state'].initial = self.instance.state

    class Meta:
        model = Profile
        fields = ['phone', 'birth_date', 'bio', 'cep', 'address', 'city', 'state']

    def save(self, commit=True):
        profile = super().save(commit=False)

        profile.user.first_name = self.cleaned_data['first_name']
        profile.user.last_name = self.cleaned_data['last_name']
        profile.user.email = self.cleaned_data['email']

        if commit:
            profile.user.save()
            profile.save()

        return profile


class CustomPasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        label='Senha Atual',
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Digite sua senha atual'}
        ),
    )

    new_password1 = forms.CharField(
        label='Nova Senha',
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Digite sua nova senha'}
        ),
        help_text='Mínimo 8 caracteres, não pode ser muito comum',
    )

    new_password2 = forms.CharField(
        label='Confirmar Nova Senha',
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Confirme sua nova senha'}
        ),
    )

    def __init__(self, user, *args, **kwargs):
        """Recebe o usuário atual para validar a senha antiga."""
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        password = self.cleaned_data.get('old_password')
        if not self.user.check_password(password):
            raise ValidationError('Senha atual inválida!')
        return password

    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        validate_password(password, self.user)

        return password

    def save(self, commit=True):
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 and self.user.check_password(new_password1):
            raise ValidationError('A nova senha não pode ser igual à senha atual!')

        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError('As senhas não coincidem.')

        return cleaned_data
