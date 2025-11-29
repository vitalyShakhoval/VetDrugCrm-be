from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import EmployeProfile
from django import forms

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Введите email.')

    class Meta:
        model = EmployeProfile
        fields = ( 'email', 'password1', 'password2')

class LoginForm(AuthenticationForm):
    username = forms.EmailField(  
        label='Почта',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    password = forms.CharField(
        label='Пароль', 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )