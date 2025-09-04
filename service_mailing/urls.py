from django.urls import path
from django.views.decorators.cache import cache_page

from service_mailing.apps import ServiceMailingConfig
# from service_mailing.views import (
    # ContactsView,
    # ProductListView,
    # ProductDetailView,
    # ProductCreateView,
    # ProductUpdateView,
    # ProductDeleteView, CategoryProductsListView,
# )

app_name = ServiceMailingConfig.name  # Извлечение имени приложения из модуля service_mailing/apps.py

urlpatterns = [
    # path("", ProductListView.as_view(), name="product_list"),  # Маршрут для главной страницы с каталогом товаров
    # path("catalog/<int:pk>/", cache_page(60)(ProductDetailView.as_view()), name="product_detail"),  # Маршрут для страницы 'Товар'
    # path("catalog/create/", ProductCreateView.as_view(), name="product_create"),  # Маршрут для страницы 'Создать товар'
    # # Маршрут для страницы 'Редактировать товар'
    # path("catalog/<int:pk>/update/", ProductUpdateView.as_view(), name="product_update"),
    # # Маршрут для страницы 'Удалить товар'
    # path("catalog/<int:pk>/delete/", ProductDeleteView.as_view(), name="product_delete"),
    # path("catalog/", ContactsView.as_view(), name="contacts"),  # Маршрут для страницы 'Контакты'
    # path("catalog/<int:pk>/category/", CategoryProductsListView.as_view(), name="category_products"),  # Маршрут для страницы 'Категория товаров'
]
