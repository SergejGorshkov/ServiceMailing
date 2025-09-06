from django.db import models
from django.urls import reverse

class Recipient(models.Model):
    """Модель получателя рассылки"""
    email = models.EmailField(
        verbose_name='Email адрес',
        unique=True,
        max_length=255,
    )
    full_name = models.CharField(
        verbose_name='ФИО',
        max_length=200,
    )
    comment = models.TextField(
        verbose_name='Комментарий',
        blank=True,
        null=True,
        help_text='Дополнительная информация о получателе'
    )
    created_at = models.DateTimeField(
        verbose_name='Дата создания получателя',
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        verbose_name='Дата обновления получателя',
        auto_now=True
    )
    is_active = models.BooleanField(
        verbose_name='Активен',
        default=True,
        help_text='(включен ли получатель в рассылки)'
    )

    class Meta:
        """Метаданные модели.
        Порядок сортировки, наименование модели в единственном и множественном числе.
        """
        verbose_name = 'Получатель'
        verbose_name_plural = 'Получатели'
        ordering = ['full_name', '-created_at']

    def __str__(self):
        """Строковое представление модели."""
        return f"{self.full_name} ({self.email})"

    def get_absolute_url(self):
        """Получение абсолютного URL модели для обеспечения единой ссылки при работе с объектом "Получатель"."""
        return reverse('service_mailing:recipient_detail', kwargs={'pk': self.pk})
