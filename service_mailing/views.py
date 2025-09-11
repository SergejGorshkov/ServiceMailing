from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .models import Recipient, Message, Mailing, MailingAttempt
from .forms import RecipientForm, MessageForm, MailingForm
from .services import send_mailing
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden


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
    template_name = 'service_mailing/recipient_list.html'
    context_object_name = 'recipients'

    def get_queryset(self):
        """Фильтрация списка получателей по правам доступа"""
        user = self.request.user # Текущий пользователь

        # Проверка для менеджеров
        if user.has_perm("service_mailing.can_view_all_recipients"):
            return Recipient.objects.all().order_by('full_name')

        else:
            # Владельцы могут просматривать только своих получателей
            return Recipient.objects.filter(owner=user).order_by('full_name')


class RecipientDetailView(LoginRequiredMixin, DetailView):
    """Подробная информация о получателе"""
    model = Recipient
    template_name = 'service_mailing/recipient_detail.html'
    context_object_name = 'recipient'

    def get_queryset(self):
        """Фильтрация по правам доступа"""
        user = self.request.user  # Текущий пользователь

        # Проверка для менеджеров
        if user.has_perm("service_mailing.can_view_all_recipients"):
            return Recipient.objects.all()

        else:
            # Владельцы могут просматривать только своих получателей
            return Recipient.objects.filter(owner=user)


class RecipientCreateView(LoginRequiredMixin, CreateView):
    """Создание нового получателя"""
    model = Recipient
    form_class = RecipientForm  # Форма для создания получателя из forms.py
    template_name = 'service_mailing/recipient_form.html'
    success_url = reverse_lazy('service_mailing:recipient_list')

    def form_valid(self, form):
        """Проверка формы перед сохранением и установка текущего пользователя владельцем Получателя"""
        form.instance.owner = self.request.user
        messages.success(self.request, 'Изменения успешно сохранены!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование получателя"""
    model = Recipient
    form_class = RecipientForm
    template_name = 'service_mailing/recipient_form.html'

    def get_dispatch(self, request, *args, **kwargs):
        """ Проверка прав доступа для редактирования получателя """
        obj = self.get_object() # Получение объекта получателя
        user = self.request.user # Текущий пользователь

        # Проверка, что пользователь не является владельцем объекта
        if user != obj.owner:
            return HttpResponseForbidden("У вас нет прав для редактирования этого объекта")
        else:
            # Вызов родительского метода UpdateView для обработки запроса
            return super().dispatch(request, *args, **kwargs)

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

    def get_dispatch(self, request, *args, **kwargs):
        """ Проверка прав доступа для удаления получателя """
        obj = self.get_object()  # Получение объекта получателя
        user = self.request.user  # Текущий пользователь

        # Проверка, что пользователь не является владельцем объекта
        if user != obj.owner:
            return HttpResponseForbidden("У вас нет прав для удаления этого объекта")
        else:
            # Вызов родительского метода DeleteView для обработки запроса
            return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Получатель успешно удален!')
        return super().delete(request, *args, **kwargs)

@login_required
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

    def get_queryset(self):
        """Фильтрация списка сообщений по правам доступа"""
        user = self.request.user # Текущий пользователь

        # Проверка для менеджеров
        if user.has_perm("service_mailing.can_view_all_messages"):
            return Message.objects.all()

        else:
            # Владельцы могут просматривать только свои сообщения
            return Message.objects.filter(owner=user)


class MessageDetailView(LoginRequiredMixin, DetailView):
    """Подробная информация о сообщении"""
    model = Message
    template_name = 'service_mailing/message_detail.html'
    context_object_name = 'message'

    def get_queryset(self):
        """Фильтрация по правам доступа"""
        user = self.request.user # Текущий пользователь

        # Проверка для менеджеров
        if user.has_perm("service_mailing.can_view_all_messages"):
            return Message.objects.all()

        else:
            # Владельцы могут просматривать только свои сообщения
            return Message.objects.filter(owner=user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    """Создание нового сообщения"""
    model = Message
    form_class = MessageForm  # Форма для создания получателя из forms.py
    template_name = 'service_mailing/message_form.html'
    success_url = reverse_lazy('service_mailing:message_list')

    def form_valid(self, form):
        """Проверка формы перед сохранением и установка текущего пользователя владельцем Сообщения"""
        form.instance.owner = self.request.user
        messages.success(self.request, 'Изменения успешно сохранены!')
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

    def get_dispatch(self, request, *args, **kwargs):
        """ Проверка прав доступа для редактирования сообщения """
        obj = self.get_object() # Получение объекта сообщения
        user = self.request.user # Текущий пользователь

        # Проверка, что пользователь не является владельцем объекта
        if user != obj.owner:
            return HttpResponseForbidden("У вас нет прав для редактирования этого объекта")
        else:
            # Вызов родительского метода UpdateView для обработки запроса
            return super().dispatch(request, *args, **kwargs)

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

    def get_dispatch(self, request, *args, **kwargs):
        """ Проверка прав доступа для удаления сообщения """
        obj = self.get_object() # Получение объекта сообщения
        user = self.request.user # Текущий пользователь

        # Проверка, что пользователь не является владельцем объекта
        if user != obj.owner:
            return HttpResponseForbidden("У вас нет прав для редактирования этого объекта")
        else:
            # Вызов родительского метода DeleteView для обработки запроса
            return super().dispatch(request, *args, **kwargs)

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
        """Фильтрация списка рассылок по правам доступа"""
        user = self.request.user  # Текущий пользователь

        # Проверка для менеджеров
        if user.has_perm("service_mailing.can_view_all_mailings"):
            queryset = Mailing.objects.all()

        else:
            # Владельцы могут просматривать только свои сообщения
            queryset = Mailing.objects.filter(owner=user)

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
        """Фильтрация по правам доступа"""
        user = self.request.user # Текущий пользователь
        # Получение queryset с оптимизацией запросов
        queryset = Mailing.objects.prefetch_related(
            'recipients',
            'message',
            'attempts',
            'attempts__recipient'
        )
        # Проверка для менеджеров
        if user.has_perm("service_mailing.can_view_all_mailings"):
            return queryset
        else:
            # Владельцы могут просматривать только свои рассылки
            return queryset.filter(owner=user)


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
        """Проверка формы перед сохранением и установка текущего пользователя владельцем Сообщения"""
        form.instance.owner = self.request.user
        messages.success(self.request, 'Изменения успешно сохранены!')
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

    def get_dispatch(self, request, *args, **kwargs):
        """ Проверка прав доступа для редактирования рассылки """
        obj = self.get_object() # Получение объекта сообщения
        user = self.request.user # Текущий пользователь

        # Проверка, что пользователь не является владельцем объекта
        if user != obj.owner:
            return HttpResponseForbidden("У вас нет прав для редактирования этого объекта")
        else:
            # Вызов родительского метода UpdateView для обработки запроса
            return super().dispatch(request, *args, **kwargs)

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

    def get_dispatch(self, request, *args, **kwargs):
        """ Проверка прав доступа для удаления рассылки """
        obj = self.get_object() # Получение объекта сообщения
        user = self.request.user # Текущий пользователь

        # Проверка, что пользователь не является владельцем объекта
        if user != obj.owner:
            return HttpResponseForbidden("У вас нет прав для редактирования этого объекта")
        else:
            # Вызов родительского метода DeleteView для обработки запроса
            return super().dispatch(request, *args, **kwargs)


##############################################################################

class MailingAttemptListView(LoginRequiredMixin, ListView):
    """Список всех попыток рассылок со статистикой"""
    model = MailingAttempt
    template_name = 'service_mailing/mailing_attempt_list.html'
    context_object_name = 'attempts'
    paginate_by = 10


    def get_queryset(self):
        """Получение queryset с оптимизацией запросов и фильтрацией по правам доступа"""
        user = self.request.user # Текущий пользователь

        # Базовый queryset
        queryset = MailingAttempt.objects.select_related(
            'mailing',  # Загрузка рассылки
            'mailing__owner',  # Загрузка владельца рассылки
            'recipient'  # Загрузка получателя
        ).order_by('-attempt_time')

        # Фильтрация по правам доступа
        if not user.has_perm("service_mailing.can_view_all_mailings"): # Если не менеджер
            # Пользователь может видеть только попытки своих рассылок
            queryset = queryset.filter(mailing__owner=user)

        # Фильтрация по статусу
        status = self.request.GET.get('status')
        if status in ['success', 'failed']:
            queryset = queryset.filter(status=status)

        return queryset


    def get_context_data(self, **kwargs):
        """Добавление дополнительного контекста"""
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Базовый QuerySet для статистики
        if user.has_perm("service_mailing.can_view_all_mailings"):
            # Менеджеры видят всю статистику
            total_attempts = MailingAttempt.objects.count()
            success_attempts = MailingAttempt.objects.filter(status='success').count()
            failed_attempts = MailingAttempt.objects.filter(status='failed').count()
            mailings = Mailing.objects.all()
        else:
            # Обычные пользователи видят только свою статистику
            user_mailings = Mailing.objects.filter(owner=user)
            total_attempts = MailingAttempt.objects.filter(mailing__in=user_mailings).count()
            success_attempts = MailingAttempt.objects.filter(mailing__in=user_mailings, status='success').count()
            failed_attempts = MailingAttempt.objects.filter(mailing__in=user_mailings, status='failed').count()
            mailings = user_mailings

        # Процент успешных отправок
        success_rate = round(success_attempts / total_attempts * 100) if total_attempts > 0 else 0

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
@login_required
def toggle_mailing_status(request, pk):
    """Переключение статуса активности рассылки"""
    mailing = get_object_or_404(Mailing, pk=pk) # Получение объекта рассылки
    # Проверка прав доступа
    user = request.user
    can_deactivate = user.has_perm('service_mailing.can_deactivate_mailing') # Проверка права на деактивацию рассылок
    is_owner = hasattr(mailing, 'owner') and mailing.owner == user # Проверка владельца рассылки

    if not (can_deactivate or is_owner):
        raise PermissionDenied("У вас нет прав для изменения статуса этой рассылки")

    mailing.is_active = not mailing.is_active
    mailing.save()

    status = "активирована" if mailing.is_active else "деактивирована"
    messages.success(request, f'Рассылка {status}')
    return redirect('service_mailing:mailing_list')

@login_required
def start_mailing_manually(request, pk):
    """Ручной запуск рассылки через интерфейс страницы 'Рассылки' """
    mailing = get_object_or_404(Mailing, pk=pk)
    user = request.user
    is_owner = hasattr(mailing, 'owner') and mailing.owner == user  # Проверка владельца рассылки
    if not is_owner:
        raise PermissionDenied("У вас нет прав для изменения статуса этой рассылки")

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
