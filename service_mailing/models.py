from django.db import models
from django.utils import timezone
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


class Message(models.Model):
    """Модель сообщения для рассылки"""
    title = models.CharField(
        max_length=150,
        verbose_name="Тема сообщения",
    )
    content = models.TextField(
        verbose_name="Содержание сообщения",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,  # Устанавливает текущую дату только при создании
        verbose_name="Дата создания сообщения",
    )
    updated_at = models.DateTimeField(
        verbose_name='Дата обновления сообщения',
        auto_now=True
    )

    class Meta:
        """Метаданные модели.
        Порядок сортировки, наименование модели в единственном и множественном числе.
        """
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['-created_at']  # Сортировка по убыванию даты создания

    def __str__(self):
        """Строковое представление модели."""
        return self.title

    def get_absolute_url(self):
        """Получение абсолютного URL модели для обеспечения единой ссылки при работе с объектом "Сообщение"."""
        return reverse('service_mailing:message_detail', kwargs={'pk': self.pk})


class Mailing(models.Model):
    """Модель рассылки"""

    # Варианты статусов рассылки
    STATUS_CHOICES = [
        ('created', 'Создана'),
        ('started', 'Запущена'),
        ('completed', 'Завершена'),
    ]
    name = models.CharField(
        verbose_name='Название рассылки',
        max_length=200,
        blank=True,
        null=True,
        help_text='Произвольное название рассылки для ее идентификации'
    )

    start_time = models.DateTimeField(
        verbose_name='Дата и время начала отправки',
        help_text='Когда начать отправку рассылки'
    )

    end_time = models.DateTimeField(
        verbose_name='Дата и время окончания отправки',
        help_text='Когда завершить отправку рассылки'
    )

    status = models.CharField(
        verbose_name='Статус',
        max_length=10,
        choices=STATUS_CHOICES,
        default='created',
        help_text='Текущий статус рассылки'
    )

    message = models.ForeignKey(
        Message,
        verbose_name='Сообщение',
        on_delete=models.CASCADE,  # Удаление сообщения при удалении рассылки
        related_name='mailings',  # переменная для обратной связи в модели Message
        help_text='Сообщение для отправки'
    )

    recipients = models.ManyToManyField(
        Recipient,
        verbose_name='Получатели',
        related_name='mailings',  # переменная для обратной связи в модели Recipient
        help_text='Список получателей рассылки'
    )

    created_at = models.DateTimeField(
        verbose_name='Дата создания рассылки',
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        verbose_name='Дата обновления рассылки',
        auto_now=True
    )

    is_active = models.BooleanField(
        verbose_name='Активна|Неактивна',
        default=True,
        help_text='Включена ли рассылка'
    )

    class Meta:
        """Метаданные модели.
        Порядок сортировки, наименование модели в единственном и множественном числе.
        """
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        ordering = ['-created_at']
        # indexes = [ # Индексы для ускорения поиска по полям
        #     models.Index(fields=['status']),
        #     models.Index(fields=['start_time', 'end_time']),
        # ]

    def __str__(self):
        """Строковое представление модели.
        Возвращает название рассылки или ее порядковый номер, если не задано ее название."""
        return self.name or f"Рассылка № {self.id}"

    def get_absolute_url(self):
        """Получение абсолютного URL модели для обеспечения единой ссылки при работе с объектом "Рассылка"."""
        return reverse('service_mailing:mailing_detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        """Автоматическое обновление статуса рассылки при сохранении"""
        if self.end_time and timezone.now() > self.end_time:
            self.status = 'completed'
        elif self.status == 'created' and self.start_time and timezone.now() >= self.start_time:
            self.status = 'started'

        # # Генерация названия если не указано
        # if not self.name:
        #     self.name = f"Рассылка {self.message.subject if self.message else ''} - {self.start_time.strftime('%d.%m.%Y')}"

        super().save(*args, **kwargs)  # Вызов базового метода save, сохранение модели в БД и обновление статуса рассылки

    @property
    def is_currently_active(self):
        """Проверка, активна ли рассылка в данный момент"""
        now = timezone.now()
        return (self.is_active and
                self.status == 'started' and
                self.start_time <= now <= self.end_time)

    @property
    def recipients_count(self):
        """Количество получателей рассылки"""
        return self.recipients.count()

    def get_status_class(self):
        """CSS класс для отображения статуса. Используется в шаблоне."""
        status_classes = {
            'created': 'secondary',
            'started': 'success',
            'completed': 'dark'
        }
        return status_classes.get(self.status, 'secondary')

    def can_be_edited(self):
        """Можно ли редактировать рассылку (можно только со статусом 'created' и 'started').
        Используется в шаблоне и views.py."""
        return self.status in ['created', 'started'] and self.is_active

    def can_be_deleted(self):
        """Можно ли удалить рассылку (удалить можно только со статусом 'created').
        Используется в шаблоне и views.py."""
        return self.status == 'created'
