from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import (
    authenticate, get_user_model, password_validation,
)
from . import validators
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.exceptions import ValidationError
User = get_user_model()


class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(max_length=50, widget=forms.PasswordInput, label="Пароль", validators=[validators.validate_password1])
    password2 = forms.CharField(max_length=50, widget=forms.PasswordInput, label="Подтверждение пароля", validators=[validators.validate_password2])

    class Meta:
        model = User
        error_css_class = 'error'
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['required'] = 'required'

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                'Пароли не совпадают'
            )
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):

    class Meta:
        error_css_class = 'error'

    login = forms.CharField(max_length=60, label='Имя пользователя')
    password = forms.CharField(max_length=50, widget=forms.PasswordInput, label='Пароль')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control mb-3'
        self.user_cache = None

    def clean(self):
        password = self.cleaned_data.get('password', None)
        login = self.cleaned_data.get('login', None)
        try:
            user = User.objects.get(username=login)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=login)
            except User.DoesNotExist:
                user = None
        if user is None:
            raise ValidationError('Неверный логин или пароль')

        if not user.check_password(password):
            raise ValidationError('Неверный логин или пароль')

        self.user_cache = user

        return self.cleaned_data

