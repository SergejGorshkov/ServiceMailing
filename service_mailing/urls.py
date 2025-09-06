from django.urls import path

from service_mailing.apps import ServiceMailingConfig
from service_mailing.views import (
    RecipientListView,
    RecipientCreateView,
    RecipientDetailView,
    RecipientUpdateView,
    RecipientDeleteView,
    toggle_recipient_status,
)

# from django.views.decorators.cache import cache_page


app_name = ServiceMailingConfig.name  # Извлечение имени приложения из модуля service_mailing/apps.py

urlpatterns = [
    # CRUD маршруты для получателей
    path('recipient/', RecipientListView.as_view(), name='recipient_list'),
    path('recipient/create/', RecipientCreateView.as_view(), name='recipient_create'),
    path('recipient/<int:pk>/', RecipientDetailView.as_view(), name='recipient_detail'),
    path('recipient/<int:pk>/edit/', RecipientUpdateView.as_view(), name='recipient_update'),
    path('recipient/<int:pk>/delete/', RecipientDeleteView.as_view(), name='recipient_delete'),

    # Дополнительные операции для изменения статуса получателя (активный/неактивный)
    path('recipient/<int:pk>/toggle-status/', toggle_recipient_status, name='recipient_toggle_status'),


    # path("catalog/<int:pk>/", cache_page(60)(ProductDetailView.as_view()), name="product_detail"),  # Маршрут для страницы 'Товар'

]
