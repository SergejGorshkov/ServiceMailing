from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from service_mailing.models import MailingAttempt


def send_mailing_email(recipient_email, subject, message):
    """Отправка одного email сообщения"""
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=False,  # Означает, что ошибки не должны прерывать отправку
        )
        return True, "Успешно отправлено"
    except Exception as error:
        return False, str(error)


def send_mailing(mailing):
    """Отправка рассылки всем получателям"""
    if not mailing.can_be_sent():
        return False, "Возможная причина: не активна, имеет статус 'Завершена', не добавлено сообщение или получатели."

    successful_sends = 0  # Счетчик успешных отправок
    total_recipients = mailing.recipients.count()  # Количество получателей
    recipients = mailing.recipients.all()  # Получение всех получателей

    for recipient in recipients:  # Перебор всех получателей и отправка им писем
        # Вызов функции отправки письма и сохранение результата в переменные success и error_message
        success, error_message = send_mailing_email(recipient.email, mailing.message.title, mailing.message.content)
        if success:  # Если отправка успешна, то увеличивается счетчик успешных отправок
            successful_sends += 1

            # Сохранение результата отправки в таблицу MailingAttempt для каждого отправленного письма
            MailingAttempt.objects.create(
                mailing=mailing,
                recipient=recipient,
                status="success",
                server_response="Письмо успешно отправлено",
                attempt_time=timezone.now(),
            )

        if not success:  # Если отправка не успешна, то сохранение ошибки в таблицу MailingAttempt
            MailingAttempt.objects.create(
                mailing=mailing,
                recipient=recipient,
                status="failed",
                server_response=error_message,
                attempt_time=timezone.now(),
            )

    return True, f"Отправлено {successful_sends} из {total_recipients} писем"
