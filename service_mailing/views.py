from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Recipient, Message, Mailing, MailingAttempt
from .forms import RecipientForm, MessageForm, MailingForm
from .services import send_mailing


class HomeView(TemplateView):
    """Главная страница со статистикой рассылок"""
    template_name = 'service_mailing/home.html'

    def get_context_data(self, **kwargs):
        """Добавление статистики в контекст"""
        context = super().get_context_data(**kwargs)

        # Получение общей статистики
        total_mailings = Mailing.objects.count() # Общее количество рассылок
        active_mailings = Mailing.objects.filter(status='started').count() # Активные (запущенные) рассылки
        unique_recipients = Recipient.objects.count() # Уникальные получатели (по email)

        # Получение дополнительной статистики по статусам рассылок
        completed_mailings = Mailing.objects.filter(status='completed').count() # Завершенные рассылки
        created_mailings = Mailing.objects.filter(status='created').count() # Созданные рассылки

        context.update({
            'total_mailings': total_mailings,
            'active_mailings': active_mailings,
            'unique_recipients': unique_recipients,
            'completed_mailings': completed_mailings,
            'created_mailings': created_mailings,
        })

        return context

##############################################################################

# Представления для управления получателями
class RecipientListView(LoginRequiredMixin, ListView):
    """Список всех получателей"""
    model = Recipient
    template_name = 'service_mailing/recipient_list.html'  # Шаблон для отображения списка получателей
    context_object_name = 'recipients'  # Переменная для передачи списка получателей в шаблон
    paginate_by = 20  # Количество записей на странице

    def get_queryset(self):
        """Фильтрация списка получателей по ФИО"""
        return Recipient.objects.all().order_by('full_name')


class RecipientDetailView(LoginRequiredMixin, DetailView):
    """Подробная информация о получателе"""
    model = Recipient
    template_name = 'service_mailing/recipient_detail.html'
    context_object_name = 'recipient'


class RecipientCreateView(LoginRequiredMixin, CreateView):
    """Создание нового получателя"""
    model = Recipient
    form_class = RecipientForm  # Форма для создания получателя из forms.py
    template_name = 'service_mailing/recipient_form.html'
    success_url = reverse_lazy('service_mailing:recipient_list')

    def form_valid(self, form):
        """Проверка формы перед сохранением"""
        messages.success(self.request, 'Получатель успешно создан!')
        return super().form_valid(form)

    def form_invalid(self, form):
        """Вывод ошибок валидации формы"""
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование получателя"""
    model = Recipient
    form_class = RecipientForm
    template_name = 'service_mailing/recipient_form.html'

    def get_success_url(self):
        return reverse_lazy('service_mailing:recipient_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Изменения успешно сохранены!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)


class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление получателя"""
    model = Recipient
    context_object_name = 'recipient'
    template_name = 'service_mailing/recipient_confirm_delete.html'
    success_url = reverse_lazy('service_mailing:recipient_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Получатель успешно удален!')
        return super().delete(request, *args, **kwargs)


def toggle_recipient_status(request, pk):
    """Переключение статуса активности получателя"""
    recipient = get_object_or_404(Recipient, pk=pk)
    recipient.is_active = not recipient.is_active
    recipient.save()

    messages.success(request, f'Статус получателя {"активирован" if recipient.is_active else "деактивирован"}')
    return redirect('service_mailing:recipient_list')

##############################################################################

# Представления для управления сообщениями
class MessageListView(LoginRequiredMixin, ListView):
    """Список всех сообщений"""
    model = Message
    template_name = 'service_mailing/message_list.html'  # Шаблон для отображения списка сообщений
    context_object_name = 'messages'  # Переменная для передачи списка сообщений в шаблон
    paginate_by = 20  # Количество записей на странице


class MessageDetailView(LoginRequiredMixin, DetailView):
    """Подробная информация о сообщении"""
    model = Message
    template_name = 'service_mailing/message_detail.html'
    context_object_name = 'message'


class MessageCreateView(LoginRequiredMixin, CreateView):
    """Создание нового сообщения"""
    model = Message
    form_class = MessageForm  # Форма для создания получателя из forms.py
    template_name = 'service_mailing/message_form.html'
    success_url = reverse_lazy('service_mailing:message_list')

    def form_valid(self, form):
        """Проверка формы перед сохранением"""
        messages.success(self.request, 'Сообщение успешно создано!')
        return super().form_valid(form)

    def form_invalid(self, form):
        """Вывод ошибок валидации формы"""
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование получателя"""
    model = Message
    form_class = MessageForm
    template_name = 'service_mailing/message_form.html'

    def get_success_url(self):
        """Возврат на страницу деталей сообщения после сохранения"""
        return reverse_lazy('service_mailing:message_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        """Проверка формы перед сохранением"""
        messages.success(self.request, 'Изменения успешно сохранены!')
        return super().form_valid(form)

    def form_invalid(self, form):
        """Вывод ошибок валидации формы"""
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление сообщения"""
    model = Message
    context_object_name = 'message'
    template_name = 'service_mailing/message_confirm_delete.html'
    success_url = reverse_lazy('service_mailing:message_list')

    def delete(self, request, *args, **kwargs):
        """Удаление сообщения"""
        messages.success(self.request, 'Сообщение успешно удалено!')
        return super().delete(request, *args, **kwargs)

##############################################################################

# Представления для управления рассылками
class MailingListView(LoginRequiredMixin, ListView):
    """Список всех рассылок"""
    model = Mailing
    template_name = 'service_mailing/mailing_list.html'
    context_object_name = 'mailings' # Переменная для передачи списка рассылок в шаблон
    paginate_by = 20

    def get_queryset(self):
        """Фильтрация списка рассылок по статусу"""
        # Загрузка всех получателей и сообщений заранее, а не по одному запросу на каждую рассылку
        queryset = Mailing.objects.all().prefetch_related('recipients', 'message')

        # Фильтрация по статусу (для выпадающего списка в шаблоне)
        status = self.request.GET.get('status')
        if status in ['created', 'started', 'completed']:
            queryset = queryset.filter(status=status)

        return queryset.order_by('-created_at') # Сортировка рассылок по дате создания (новые сверху)

    def get_context_data(self, **kwargs):
        """ Добавление данных в контекст для фильтрации по статусу в шаблоне mailing_list.html"""
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '') # Получение статуса рассылки из GET-запроса для фильтрации в шаблоне mailing_list.html
        return context


class MailingDetailView(LoginRequiredMixin, DetailView):
    """Детальная информация о рассылке"""
    model = Mailing
    template_name = 'service_mailing/mailing_detail.html'
    context_object_name = 'mailing'

    def get_queryset(self):
        """Предварительная загрузка всех получателей и сообщений из БД"""
        return Mailing.objects.prefetch_related(
            'recipients',  # Загрузка всех получателей
            'message',  # Загрузка сообщения
            'attempts',  # Загрузка всех попыток отправки
            'attempts__recipient'  # Загрузка получателя для каждой попытки
        )

    def get_context_data(self, **kwargs):
        """Добавление данных в контекст для отображения статистики в шаблоне mailing_detail.html"""
        context = super().get_context_data(**kwargs)
        mailing = self.object # Получение текущей рассылки из контекста

        total_attempts = MailingAttempt.objects.filter(mailing=mailing).count() # Общее количество попыток отправки
        success_attempts = MailingAttempt.objects.filter(mailing=mailing, status='success').count() # Успешные попытки
        failed_attempts = MailingAttempt.objects.filter(mailing=mailing, status='failed').count() # Неуспешные попытки

        context.update({
            'total_attempts': total_attempts,
            'success_attempts': success_attempts,
            'failed_attempts': failed_attempts
        })

        return context


class MailingCreateView(LoginRequiredMixin, CreateView):
    """Создание новой рассылки"""
    model = Mailing
    form_class = MailingForm
    template_name = 'service_mailing/mailing_form.html'
    success_url = reverse_lazy('service_mailing:mailing_list')

    def form_valid(self, form):
        """Проверка формы перед сохранением"""
        messages.success(self.request, 'Рассылка успешно создана!')
        return super().form_valid(form)

    def form_invalid(self, form):
        """Вывод ошибок валидации формы"""
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование рассылки"""
    model = Mailing
    form_class = MailingForm
    template_name = 'service_mailing/mailing_form.html'

    def get_success_url(self):
        """Возврат на страницу деталей рассылки после сохранения"""
        return reverse_lazy('service_mailing:mailing_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        """Проверка формы перед сохранением"""
        messages.success(self.request, 'Изменения успешно сохранены!')
        return super().form_valid(form)

    def form_invalid(self, form):
        """Вывод ошибок валидации формы"""
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)

    def get_form(self, form_class=None):
        """Добавление readonly полей для завершенных рассылок"""
        form = super().get_form(form_class)
        if self.object.status == 'completed':
            for field in form.fields:
                form.fields[field].widget.attrs['readonly'] = True
                form.fields[field].widget.attrs['disabled'] = True
        return form


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление рассылки"""
    model = Mailing
    template_name = 'service_mailing/mailing_confirm_delete.html'
    success_url = reverse_lazy('service_mailing:mailing_list')
    context_object_name = 'mailing'


##############################################################################

class MailingAttemptListView(LoginRequiredMixin, ListView):
    """Список всех попыток рассылок со статистикой"""
    model = MailingAttempt
    template_name = 'service_mailing/mailing_attempt_list.html'
    context_object_name = 'attempts'
    paginate_by = 10

    def get_queryset(self):
        """Получение queryset с оптимизацией запросов и фильтрацией"""
        queryset = MailingAttempt.objects.select_related(
            'mailing',
            'recipient'
        ).order_by('-attempt_time')

        # Фильтрация по статусу
        status = self.request.GET.get('status')
        if status in ['success', 'failed']:
            queryset = queryset.filter(status=status)

        return queryset


    def get_context_data(self, **kwargs):
        """Добавление дополнительного контекста"""
        context = super().get_context_data(**kwargs)

        # Статистика
        total_attempts = MailingAttempt.objects.count()
        success_attempts = MailingAttempt.objects.filter(status='success').count()
        failed_attempts = MailingAttempt.objects.filter(status='failed').count()

        # Процент успешных отправок
        success_rate = round(success_attempts / total_attempts * 100) if total_attempts > 0 else 0

        # Список рассылок для фильтра
        mailings = Mailing.objects.all()

        # Добавление статистики в контекст для шаблона mailing_attempt_list.html
        context.update({
            'total_attempts': total_attempts, # Общее количество попыток
            'success_attempts': success_attempts, # Успешные попытки
            'failed_attempts': failed_attempts, # Неуспешные попытки
            'success_rate': success_rate, # Процент успешных отправок
            'mailings': mailings, # Список рассылок для фильтра


            'status_filter': self.request.GET.get('status', ''), # Фильтр по статусу
            'mailing_filter': self.request.GET.get('mailing', ''), # Фильтр по ID рассылки
            'search_query': self.request.GET.get('search', ''), # Поиск по получателям
        })

        return context


# Дополнительные функции
def toggle_mailing_status(request, pk):
    """Переключение статуса активности рассылки"""
    mailing = get_object_or_404(Mailing, pk=pk)
    mailing.is_active = not mailing.is_active
    mailing.save()

    status = "активирована" if mailing.is_active else "деактивирована"
    messages.success(request, f'Рассылка {status}')
    return redirect('service_mailing:mailing_list')


def start_mailing_manually(request, pk):
    """Ручной запуск рассылки через интерфейс страницы 'Рассылки' """
    mailing = get_object_or_404(Mailing, pk=pk)

    # Смена статуса и сохранение его в БД
    mailing.status = 'started'
    mailing.save()

    # Отправка рассылки
    success, result_message = send_mailing(mailing) # Отправка рассылки (вызов функции из services.py)

    if success:
        messages.success(request, f'Рассылка запущена! {result_message}')
        mailing.status = 'completed' # Смена статуса рассылки на 'Завершена' после успешной отправки
        mailing.save()
    else:
        messages.error(request, f'Ошибка отправки. {result_message}')
        mailing.status = 'created' # Возврат статуса рассылки в исходное значение
        mailing.save()

    return redirect('service_mailing:mailing_list')

