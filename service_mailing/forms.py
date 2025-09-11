from django import forms
from django.utils import timezone
from .models import Recipient, Message, Mailing
from django.core.exceptions import ValidationError


class RecipientForm(forms.ModelForm):
    """Форма для создания и редактирования получателей"""

    class Meta:
        """Мета-класс для настройки формы"""

        model = Recipient
        fields = ["email", "full_name", "comment", "is_active"]  # поля для отображения в форме
        # настройки виджета для каждого поля
        widgets = {
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "example@mail.com",
                }
            ),
            "full_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Иванов Иван Иванович",
                }
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Дополнительная информация о получателе",
                }
            ),
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }
        labels = {
            "email": "Email адрес",
            "full_name": "ФИО",
            "comment": "Комментарий",
            "is_active": "Статус активности",
        }
        # help_texts = {
        #     'email': 'Уникальный email адрес получателя',
        # }


class MessageForm(forms.ModelForm):
    """Форма для создания и редактирования сообщений"""

    class Meta:
        """Мета-класс для настройки формы"""

        model = Message
        fields = ["title", "content"]  # поля для отображения в форме
        # настройки виджета для каждого поля
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Тема сообщения",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 10,
                    "placeholder": "Текст сообщения",
                }
            ),
        }
        labels = {
            "title": "Тема сообщения",
            "content": "Текст сообщения",
        }


class MailingForm(forms.ModelForm):
    """Форма для создания и редактирования рассылок"""

    def __init__(self, *args, **kwargs):
        """Инициализация формы"""
        super().__init__(*args, **kwargs)

    class Meta:
        """Мета-класс для настройки полей формы"""

        model = Mailing
        fields = ["name", "message", "recipients", "start_time", "end_time", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Название рассылки"}),
            "message": forms.Select(attrs={"class": "form-select"}),
            "recipients": forms.SelectMultiple(attrs={"class": "form-select", "size": "10"}),
            "start_time": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "end_time": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "name": "Название рассылки",
            "message": "Сообщение",
            "recipients": "Получатели",
            "start_time": "Время начала отправки",
            "end_time": "Время окончания отправки",
            "is_active": "Активна",
        }
        help_texts = {"recipients": "Выберите получателей (удерживайте Ctrl для множественного выбора)"}

    def clean(self):
        """Проверка данных перед сохранением"""
        cleaned_data = super().clean()  # получение очищенных данных из родительского класса
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and end_time:
            if start_time >= end_time:
                raise ValidationError("Время окончания рассылки должно быть позже времени ее начала")

            if start_time < timezone.now():
                raise ValidationError("Время начала не может быть в прошлом")

        return cleaned_data
