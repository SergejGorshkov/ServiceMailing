from django.core.management.base import BaseCommand
from service_mailing.models import Mailing
from service_mailing.services import send_mailing


class Command(BaseCommand):
    help = 'Запуск рассылок вручную через командную строку'

    def add_arguments(self, parser):
        """ Функция для добавления аргументов командной строки """
        parser.add_argument(
            '--mailing-id', # Добавление аргумента --mailing-id из командной строки для указания ID рассылки
            type=int, # Тип аргумента
            help='ID конкретной рассылки для отправки' # Подсказка для аргумента
        )

    def handle(self, *args, **options):
        """ Функция обработки аргументов командной строки.
         Принимает аргументы командной строки и опции."""
        mailing_id = options.get('mailing_id') # Получение ID рассылки из опций

        # Если указан ID рассылки...
        if mailing_id:
            # Отправка конкретной рассылки
            try:
                mailing = Mailing.objects.get(pk=mailing_id)
                self.stdout.write(f"Отправка рассылки #{mailing_id}: {mailing}")

                success, message = send_mailing(mailing) #Отправка рассылки (вызов функции send_mailing из services.py)
                if success:
                    self.stdout.write(self.style.SUCCESS(f"Успешно: {message}"))
                else:
                    self.stdout.write(self.style.ERROR(f"Ошибка: {message}"))

            except Mailing.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Рассылка с ID {mailing_id} не найдена"))

        else:
            self.stdout.write(self.style.WARNING(
                "Для отправки конкретной рассылки укажите ее ID (напр., python manage.py send_mailing --mailing-id 1)"
            ))
