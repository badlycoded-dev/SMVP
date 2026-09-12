from django import forms
from django.contrib.auth import get_user_model
from .models import (
    SellerApplication, Company, Comment, Proposition, PropositionComment, SiteAnnouncement,
)


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        label="Ім'я",
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': "Ваше ім'я",
        })
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': "your@email.com",
        })
    )
    subject = forms.CharField(
        max_length=200,
        label="Тема",
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': "Тема повідомлення",
        })
    )
    message = forms.CharField(
        label="Повідомлення",
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'placeholder': "Ваше повідомлення...",
            'rows': 6,
        })
    )


class SellerApplicationForm(forms.ModelForm):
    class Meta:
        model = SellerApplication
        fields = ['company_name', 'message']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': "Назва компанії"}),
            'message': forms.Textarea(attrs={'class': 'form-input', 'rows': 5, 'placeholder': "Чому ви хочете продавати?"}),
        }
        labels = {
            'company_name': "Назва компанії",
            'message': "Опишіть, що плануєте продавати",
        }


class SellerApplicationReviewForm(forms.Form):
    ACTION_CHOICES = [('approve', 'Схвалити'), ('reject', 'Відхилити')]

    action = forms.ChoiceField(choices=ACTION_CHOICES, widget=forms.RadioSelect)
    review_note = forms.CharField(
        required=False, label="Коментар",
        widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
    )


class CompanyDetailsForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'slug', 'description', 'logo', 'is_single']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'slug': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-input'}),
        }
        labels = {
            'is_single': "Я продаю самостійно (не команда/організація)",
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': "Ваш коментар..."}),
        }
        labels = {'body': ''}


class PropositionForm(forms.ModelForm):
    class Meta:
        model = Proposition
        fields = ['title', 'body']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': "Тема пропозиції"}),
            'body': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': "Опишіть вашу пропозицію..."}),
        }
        labels = {'title': "Тема", 'body': "Опис"}


class PropositionCommentForm(forms.ModelForm):
    class Meta:
        model = PropositionComment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': "Ваш коментар..."}),
        }
        labels = {'body': ''}


class PropositionDecisionForm(forms.Form):
    STATUS_CHOICES = [
        ('approved', 'Схвалити'),
        ('declined', 'Відхилити'),
    ]
    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.RadioSelect)
    decision_note = forms.CharField(
        label="Пояснення",
        widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
    )

class AddMemberForm(forms.Form):
    username = forms.CharField(
        label="Ім'я користувача",
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': "username"}),
    )

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        User = get_user_model()
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError("Користувача не знайдено.")


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = SiteAnnouncement
        fields = ['title', 'body']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'body': forms.Textarea(attrs={'class': 'form-input', 'rows': 5}),
        }
        labels = {'title': "Заголовок", 'body': "Текст"}
