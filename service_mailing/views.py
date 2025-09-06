from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Recipient
from .forms import RecipientForm


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


# Дополнительные функции для AJAX или простых операций
def toggle_recipient_status(request, pk):
    """Переключение статуса активности получателя"""
    recipient = get_object_or_404(Recipient, pk=pk)
    recipient.is_active = not recipient.is_active
    recipient.save()

    messages.success(request, f'Статус получателя {"активирован" if recipient.is_active else "деактивирован"}')
    return redirect('service_mailing:recipient_list')
