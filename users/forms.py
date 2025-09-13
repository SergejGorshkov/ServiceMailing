from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .models import User


class CustomUserCreationForm(UserCreationForm):
    """Форма для создания пользователя"""

    class Meta:
        """Мета-класс для настройки формы"""

        model = User
        fields = ["username", "email", "phone", "avatar", "country", "password1", "password2"]
        widgets = {
            "avatar": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/jpeg, image/png, .jpg, .jpeg, .png",
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super(self).__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update({"class": "form-control", "placeholder": "Введите никнейм"})
        self.fields["email"].widget.attrs.update({"class": "form-control", "placeholder": "Введите email"})
        self.fields["phone"].widget.attrs.update({"class": "form-control", "placeholder": "Введите номер телефона"})
        self.fields["avatar"].widget.attrs.update(
            {
                "class": "form-control",
                "accept": "image/jpeg, image/png, .jpg, .jpeg, .png",  # только изображения в формате jpeg, png
                "placeholder": "Загрузите изображение в формате jpeg, png, jpg",
            }
        )
        self.fields["country"].widget.attrs.update({"class": "form-control", "placeholder": "Введите страну"})
        self.fields["password1"].widget.attrs.update({"class": "form-control", "placeholder": "Введите пароль"})
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите пароль повторно"}
        )

        # Делаем email readonly, так как он используется для входа
        self.fields["email"].widget.attrs["readonly"] = True

    def clean_email(self):
        """Валидация email на уникальность"""
        email = self.cleaned_data.get("email")

        if not email:
            raise ValidationError("Email обязателен для заполнения")

        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким email уже существует")

        return email

    def clean_avatar(self):
        """Валидация загружаемого изображения"""
        avatar = self.cleaned_data.get("avatar")

        # Если изображение не загружено (т.к. поле не обязательно)
        if not avatar:
            return None

        # Проверка размера файла (максимум 5 МБ)
        max_size = 5 * 1024 * 1024  # 5 МБ в байтах
        if avatar.size > max_size:
            raise ValidationError(
                f"Размер файла слишком большой. Максимальный размер: 5 МБ. "
                f"Ваш файл: {avatar.size // 1024 // 1024} МБ"
            )

        # Проверка формата файла по расширению
        valid_extensions = ["jpg", "jpeg", "png"]
        extension = avatar.name.split(".")[-1].lower()  # получение расширения файла

        if extension not in valid_extensions:
            raise ValidationError(f"Неподдерживаемый формат файла. Ваш файл: {extension}")

        return avatar


class UserProfileForm(forms.ModelForm):
    """Форма для редактирования профиля пользователя"""

    class Meta:
        """Мета-класс для настройки формы"""

        model = User
        fields = ["username", "email", "phone", "avatar", "country"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Введите имя пользователя"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Введите email"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "+79999999999"}),
            "country": forms.TextInput(attrs={"class": "form-control", "placeholder": "Введите страну"}),
            "avatar": forms.ClearableFileInput(
                attrs={"class": "form-control", "accept": "image/jpeg, image/png, .jpg, .jpeg, .png"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем email readonly, так как он используется для входа
        self.fields["email"].widget.attrs["readonly"] = True

    def clean_avatar(self):
        """Валидация аватара"""
        avatar = self.cleaned_data.get("avatar")

        if not avatar:
            return None

        # Проверка размера файла (максимум 5 МБ)
        max_size = 5 * 1024 * 1024
        if avatar.size > max_size:
            raise forms.ValidationError("Размер файла слишком большой. Максимальный размер: 5 МБ")

        # Проверка формата файла
        valid_extensions = ["jpg", "jpeg", "png"]
        extension = avatar.name.split(".")[-1].lower()

        if extension not in valid_extensions:
            raise forms.ValidationError(f"Неподдерживаемый формат файла. Разрешены: {', '.join(valid_extensions)}")

        return avatar
