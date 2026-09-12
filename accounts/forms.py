from django import forms
from django.contrib.auth.models import User
from .models import Profile


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
        }
        labels = {
            'first_name': "Ім'я",
            'last_name': 'Прізвище',
            'email': 'Email',
        }


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'bio', 'birth_date', 'location', 'website', 'email_notifications']
        widgets = {
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-input'}),
            'bio': forms.Textarea(attrs={'class': 'form-input'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'location': forms.TextInput(attrs={'class': 'form-input'}),
            'website': forms.URLInput(attrs={'class': 'form-input'}),
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
        labels = {
            'avatar': 'Аватар',
            'bio': 'Про себе',
            'birth_date': 'Дата народження',
            'location': 'Місто',
            'website': 'Веб-сайт',
            'email_notifications': 'Дублювати сповіщення на email',
        }