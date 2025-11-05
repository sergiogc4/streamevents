# users/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model, authenticate
import re

CustomUser = get_user_model()


class CustomUserCreationForm(forms.ModelForm):
    """Formulari de registre d'usuaris nous"""
    password1 = forms.CharField(
        label="Contrasenya",
        widget=forms.PasswordInput,
        help_text="Ha de tenir almenys 8 caràcters, amb números i lletres."
    )
    password2 = forms.CharField(
        label="Repeteix la contrasenya",
        widget=forms.PasswordInput
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.match(r'^[\w.@+-]+$', username):
            raise ValidationError("El nom d’usuari conté caràcters no permesos.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Ja existeix un compte amb aquest correu.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Les contrasenyes no coincideixen.")

        validate_password(password1)
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class CustomUserUpdateForm(forms.ModelForm):
    """Formulari per editar el perfil"""
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'display_name', 'bio', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }


class CustomAuthenticationForm(AuthenticationForm):
    """Login amb email o username"""
    username = forms.CharField(label="Usuari o correu electrònic")

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        # Permetre login amb email o username
        user = authenticate(self.request, username=username, password=password)
        if user is None:
            try:
                user_obj = CustomUser.objects.get(email=username)
                user = authenticate(self.request, username=user_obj.username, password=password)
            except CustomUser.DoesNotExist:
                pass

        if user is None:
            raise ValidationError("Credencials incorrectes. Revisa usuari/correu i contrasenya.")

        self.user_cache = user
        return self.cleaned_data
