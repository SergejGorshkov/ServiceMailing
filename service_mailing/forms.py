from django import forms
from .models import Recipient


class RecipientForm(forms.ModelForm):
    """Форма для создания и редактирования получателей"""

    class Meta:
        """Мета-класс для настройки формы"""
        model = Recipient
        fields = ['email', 'full_name', 'comment', 'is_active']  # поля для отображения в форме
        # настройки виджета для каждого поля
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@mail.com',
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Иванов Иван Иванович',
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Дополнительная информация о получателе',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
        labels = {
            'email': 'Email адрес',
            'full_name': 'ФИО',
            'comment': 'Комментарий',
            'is_active': 'Статус активности',
        }
        # help_texts = {
        #     'email': 'Уникальный email адрес получателя',
        # }
