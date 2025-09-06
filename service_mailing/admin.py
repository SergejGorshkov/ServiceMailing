from django.contrib import admin
from .models import Recipient

@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    """Админка для модели Recipient"""
    list_display = ['email', 'full_name', 'is_active', 'created_at'] # Отображение полей в таблице админки
    list_filter = ['is_active', 'created_at'] # Фильтрация по is_active и created_at
    search_fields = ['email', 'full_name'] # Поиск по email и full_name
    list_editable = ['is_active'] # Редактирование поля is_active в админке
