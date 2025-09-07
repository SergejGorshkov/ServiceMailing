from django.urls import path

from service_mailing.apps import ServiceMailingConfig
from service_mailing.views import (
    RecipientListView,
    RecipientCreateView,
    RecipientDetailView,
    RecipientUpdateView,
    RecipientDeleteView,
    toggle_recipient_status,
    MessageListView,
    MessageDetailView,
    MessageCreateView,
    MessageUpdateView,
    MessageDeleteView,
    MailingListView,
    MailingDetailView,
    MailingCreateView,
    MailingUpdateView,
    MailingDeleteView,
    toggle_mailing_status,
    start_mailing_manually,


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

    # CRUD маршруты для сообщений
    path('message/', MessageListView.as_view(), name='message_list'),
    path('message/<int:pk>/', MessageDetailView.as_view(), name='message_detail'),
    path('message/create/', MessageCreateView.as_view(), name='message_create'),
    path('message/<int:pk>/edit/', MessageUpdateView.as_view(), name='message_update'),
    path('message/<int:pk>/delete/', MessageDeleteView.as_view(), name='message_delete'),

    # CRUD маршруты для рассылок
    path('mailing/', MailingListView.as_view(), name='mailing_list'),
    path('mailing/create/', MailingCreateView.as_view(), name='mailing_create'),
    path('mailing/<int:pk>/', MailingDetailView.as_view(), name='mailing_detail'),
    path('mailing/<int:pk>/edit/', MailingUpdateView.as_view(), name='mailing_update'),
    path('mailing/<int:pk>/delete/', MailingDeleteView.as_view(), name='mailing_delete'),

    # Дополнительные операции
    path('mailing/<int:pk>/toggle-status/', toggle_mailing_status, name='mailing_toggle_status'),
    path('mailing/<int:pk>/start/', start_mailing_manually, name='mailing_start_manual'),

    # path("catalog/<int:pk>/", cache_page(60)(ProductDetailView.as_view()), name="product_detail"),  # Маршрут для страницы 'Товар'

]
