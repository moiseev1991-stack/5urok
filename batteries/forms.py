from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import BatterySubmission


class UserRegistrationForm(UserCreationForm):
    """Форма регистрации пользователя"""
    email = forms.EmailField(required=False, label='Email', widget=forms.EmailInput(attrs={
        'class': 'form-control'
    }))
    username = forms.CharField(label='Имя пользователя', widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        labels = {
            'username': 'Имя пользователя',
        }
        widgets = {
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }


class BatterySubmissionForm(forms.ModelForm):
    """Форма для ввода информации о сданных батарейках"""
    
    class Meta:
        model = BatterySubmission
        fields = ['quantity', 'date_submitted']
        labels = {
            'quantity': 'Количество батареек',
            'date_submitted': 'Дата сдачи',
        }
        widgets = {
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Введите количество'
            }),
            'date_submitted': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }
