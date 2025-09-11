from django.db import models
from django.utils import timezone

from config import settings


class Recipient(models.Model):
    """Модель получателя рассылки"""

    email = models.EmailField(
        verbose_name="Email адрес",
        unique=True,
        max_length=255,
    )
    full_name = models.CharField(
        verbose_name="ФИО",
        max_length=200,
    )
    comment = models.TextField(
        verbose_name="Комментарий", blank=True, null=True, help_text="Дополнительная информация о получателе"
    )
    created_at = models.DateTimeField(verbose_name="Дата создания получателя", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Дата обновления получателя", auto_now=True)
    is_active = models.BooleanField(
        verbose_name="Активен", default=True, help_text="(включен ли получатель в рассылки)"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # связь с пользователем, который создал получателя (имя - из settings.py)
        on_delete=models.CASCADE,  # если пользователь удален, то поле owner будет очищено
        verbose_name="Владелец получателя",
        blank=True,
        null=True,
        related_name="recipients",  # имя поля в модели User для связи с моделью Recipient
    )

    class Meta:
        """Метаданные модели.
        Порядок сортировки, наименование модели в единственном и множественном числе.
        """

        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"
        ordering = ["full_name", "-created_at"]
        permissions = [
            ("can_view_all_recipients", "Может просматривать всех получателей"),
        ]

    def __str__(self):
        """Строковое представление модели."""
        return f"{self.full_name} ({self.email})"


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
    updated_at = models.DateTimeField(verbose_name="Дата обновления сообщения", auto_now=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # связь с пользователем, который создал получателя (имя - из settings.py)
        on_delete=models.CASCADE,  # если пользователь удален, то поле owner будет очищено
        verbose_name="Владелец сообщения",
        blank=True,
        null=True,
        related_name="messages",  # имя поля в модели User для связи с моделью Message
    )

    class Meta:
        """Метаданные модели.
        Порядок сортировки, наименование модели в единственном и множественном числе.
        """

        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ["-created_at"]  # Сортировка по убыванию даты создания
        permissions = [
            ("can_view_all_messages", "Может просматривать все сообщения"),
        ]

    def __str__(self):
        """Строковое представление модели."""
        return self.title


class Mailing(models.Model):
    """Модель рассылки"""

    # Варианты статусов рассылки
    STATUS_CHOICES = [
        ("created", "Создана"),
        ("started", "Запущена"),
        ("completed", "Завершена"),
    ]
    name = models.CharField(
        verbose_name="Название рассылки",
        max_length=200,
        blank=True,
        null=True,
    )

    start_time = models.DateTimeField(
        verbose_name="Дата и время начала отправки",
    )

    end_time = models.DateTimeField(
        verbose_name="Дата и время окончания отправки",
    )

    status = models.CharField(
        verbose_name="Статус",
        max_length=10,
        choices=STATUS_CHOICES,
        default="created",
        help_text="Текущий статус рассылки",
    )

    message = models.ForeignKey(
        Message,
        verbose_name="Сообщение",
        on_delete=models.CASCADE,  # Удаление сообщения при удалении рассылки
        related_name="mailings",  # переменная для обратной связи в модели Message
    )

    recipients = models.ManyToManyField(
        Recipient,
        verbose_name="Получатели",
        related_name="mailings",  # переменная для обратной связи в модели Recipient
        help_text="Список получателей рассылки",
    )

    created_at = models.DateTimeField(verbose_name="Дата создания рассылки", auto_now_add=True)

    updated_at = models.DateTimeField(verbose_name="Дата обновления рассылки", auto_now=True)

    is_active = models.BooleanField(verbose_name="Активна|Неактивна", default=True, help_text="(включена ли рассылка)")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # связь с пользователем, который создал получателя (имя - из settings.py)
        on_delete=models.CASCADE,  # если пользователь удален, то поле owner будет очищено
        verbose_name="Владелец рассылки",
        blank=True,
        null=True,
        related_name="mailings",  # имя поля в модели User для связи с моделью Mailing
    )

    class Meta:
        """Метаданные модели.
        Порядок сортировки, наименование модели в единственном и множественном числе.
        """

        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ["-created_at"]
        permissions = [
            ("can_view_all_mailings", "Может просматривать все рассылки"),
            ("can_deactivate_mailing", "Может отключать рассылки"),
        ]

    def __str__(self):
        """Строковое представление модели.
        Возвращает название рассылки или ее порядковый номер, если не задано ее название."""
        return self.name or f"№{self.pk}"

    def save(self, *args, **kwargs):
        """Автоматическое обновление статуса рассылки при сохранении"""
        if self.end_time and timezone.now() > self.end_time:
            self.status = "completed"
        elif self.status == "created" and self.start_time and timezone.now() >= self.start_time:
            self.status = "started"

        super().save(
            *args, **kwargs
        )  # Вызов базового метода save, сохранение модели в БД и обновление статуса рассылки

    @property
    def recipients_count(self):
        """Количество получателей рассылки"""
        return self.recipients.count()

    def get_status_class(self):
        """CSS класс для подсветки статуса рассылки. Используется в шаблоне mailing_list.html."""
        status_classes = {"created": "secondary", "started": "success", "completed": "dark"}
        return status_classes.get(self.status, "secondary")

    def can_be_sent(self):
        """Можно ли отправить рассылку"""
        return (
            self.is_active  # активна ли рассылка
            and self.status in ["created", "started"]  # статус рассылки (создана или запущена)
            and self.message is not None  # есть сообщение для рассылки
            and self.recipients.exists()  # есть хотя бы один получатель
        )


class MailingAttempt(models.Model):
    """Модель попытки отправки рассылки"""

    STATUS_CHOICES = [
        ("success", "Успешно"),
        ("failed", "Не успешно"),
    ]

    attempt_time = models.DateTimeField(verbose_name="Дата и время попытки", auto_now_add=True)

    status = models.CharField(verbose_name="Статус попытки", max_length=10, choices=STATUS_CHOICES)

    server_response = models.TextField(
        verbose_name="Ответ почтового сервера", blank=True, null=True, help_text="Ответ от почтового сервера"
    )

    mailing = models.ForeignKey(Mailing, verbose_name="Рассылка", on_delete=models.CASCADE, related_name="attempts")

    recipient = models.ForeignKey(
        Recipient, verbose_name="Получатель", on_delete=models.CASCADE, related_name="attempts", null=True, blank=True
    )

    class Meta:
        """Метаданные модели.
        Порядок сортировки, наименование модели в единственном и множественном числе, поиск по полям.
        """

        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылок"
        ordering = ["-attempt_time"]
        indexes = [
            models.Index(fields=["attempt_time"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Попытка '{self.mailing}' - {self.attempt_time}"
