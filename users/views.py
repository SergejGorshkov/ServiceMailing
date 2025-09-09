import secrets  # Генерация криптографически безопасных случайных токенов

from django.core.mail import send_mail  # Отправка email
from django.shortcuts import get_object_or_404, redirect  # HTTP-редиректы
from django.urls import reverse_lazy, reverse  # Генерация URL
from django.views.generic.edit import CreateView  # CBV для создания объектов

from config.settings import EMAIL_HOST_USER  # Получение email отправителя из settings.py
from .forms import CustomUserCreationForm  # Импорт формы регистрации
from .models import User  # Импорт модели пользователя


class RegisterView(CreateView):
    """ Класс представления регистрации пользователя """
    model = User  # Модель для создания пользователя
    template_name = 'users/register.html'  # Имя шаблона регистрации
    form_class = CustomUserCreationForm  # Используемый класс формы для регистрации
    success_url = reverse_lazy('service_mailing:home')  # После успешной регистрации перенаправляем на главную страницу

    def form_valid(self, form):
        """ Переопределение метода для отправки письма с подтверждением email """
        # Сохранение пользователя без его активации
        user = form.save()
        user.is_active = False  # Аккаунт заблокирован до подтверждения email

        token = secrets.token_urlsafe(32)  # Генерирование случайного токена для подтверждения email (32 символа)
        user.token = token  # Сохранение токена в поле модели пользователя
        user.save()
        host = self.request.get_host()  # Получение домена сайта (например: "mysite.com")
        url = f"http://{host}/users/email-confirm/{token}/"  # Ссылка для подтверждения email

        # Отправка письма со ссылкой для подтверждения email
        send_mail(
            subject="Подтверждение email",  # Тема письма
            message=f"Перейдите по ссылке {url}",  # Текст письма
            from_email=EMAIL_HOST_USER,  # Email отправителя (из settings.py)
            recipient_list=[user.email],  # Список Email получателей
        )

def email_verification(request, token):
    """ Проверка токена для подтверждения email """
    user = get_object_or_404(User, token=token)  # Получение пользователя из БД по временному токену
    user.is_active = True  # Активация аккаунта
    user.save()
    return redirect(reverse("users:login"))  # Перенаправление на страницу входа
