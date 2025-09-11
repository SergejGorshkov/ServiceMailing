from django.contrib import admin
from .models import Recipient, Message, Mailing, MailingAttempt


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    """Админка для модели Recipient"""

    list_display = (
        "email",
        "full_name",
        "is_active",
        "created_at",
    )  # Отображение полей в таблице админки
    list_filter = (
        "is_active",
        "created_at",
    )  # Фильтрация по is_active и created_at
    search_fields = (
        "email",
        "full_name",
        "comment",
    )  # Поиск по email, full_name и комментарию
    list_editable = ("is_active",)  # Редактирование поля is_active в админке
    readonly_fields = (
        "created_at",
        "updated_at",
    )  # Поля, которые нельзя редактировать


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Админка для модели Сообщение"""

    list_display = ("title", "content", "created_at", "updated_at")
    list_filter = ("created_at",)
    search_fields = ("title", "content")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    """Админка для модели Mailing"""

    list_display = ("name", "status", "message", "start_time", "end_time", "is_active", "created_at")
    list_filter = ("status", "is_active", "start_time", "end_time", "created_at")
    search_fields = ("name", "message__title")
    list_editable = ("is_active",)
    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    """Админка для модели MailingAttempt"""

    list_display = (
        "mailing",
        "recipient",
        "status",
        "attempt_time",
    )
    list_filter = ("status", "attempt_time", "mailing")
    search_fields = ("mailing__name", "recipient__email", "recipient__full_name", "server_response")
    readonly_fields = ("attempt_time",)
