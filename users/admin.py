from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # Отображаемые поля
    list_display = (
        "id",
        "email",
        "phone",
        "avatar",
        "country",
    )
    # возможность фильтрации
    list_filter = (
        "id",
        "country",
    )
    # возможность поиска по полям
    search_fields = (
        "country",
        "email",
    )
