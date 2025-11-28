from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Обязательное поле. Введите действующий email.')

    class Meta:
        model = User
        fields = ( 'email', 'password1', 'password2')

class LoginForm(AuthenticationForm):
    email = forms.EmailField(label='Почта')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)