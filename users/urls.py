from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path


from users.apps import UsersConfig
from .views import RegisterView, email_verification, UserProfileView, UserProfileUpdateView

app_name = UsersConfig.name  # Извлечение имени приложения из модуля users/apps.py

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),  # Регистрация пользователя
    path("login/", LoginView.as_view(template_name="users/login.html"), name="login"),  # Вход в учетную запись
    path(
        "email-confirm/<str:token>/", email_verification, name="email-confirm"
    ),  # Подтверждение email адреса по токену
    path("logout/", LogoutView.as_view(next_page="service_mailing:home"), name="logout"),  # Выход из учетной записи
    path("profile/", UserProfileView.as_view(), name="profile"),  # Профиль пользователя
    path("profile/edit/", UserProfileUpdateView.as_view(), name="profile_edit"),  # Редактирование профиля
]
