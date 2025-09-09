from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=False,  # Не уникальное поле
        blank=True,  # Разрешаем пустое значение
        null=True,  # Разрешаем NULL в базе
        verbose_name='Имя пользователя',
        help_text='Необязательное поле'
    )
    email = models.EmailField(
        unique=True,
        verbose_name='Email',
        max_length=254
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='Номер телефона',
        help_text='Введите номер телефона в формате: +79999999999'
    )
    avatar = models.ImageField(
        upload_to='users/avatars/',
        blank=True,
        null=True,
        verbose_name='Аватар',
        help_text='Загрузите изображение аватара')
    country = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Страна',
        help_text='Введите страну')
    # Поле для хранения токена временного доступа (для регистрации пользователя)
    token = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        verbose_name='Токен подтверждения'
    )

    USERNAME_FIELD = 'email'  # Обязательное поле для авторизации по email
    REQUIRED_FIELDS = ['username']  # Обязательные поля для создания суперпользователя (кроме email)

    class Meta:
        """ Метаданные модели """
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email
