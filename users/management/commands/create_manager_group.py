from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

from users.models import User


class Command(BaseCommand):
    help = 'Добавление прав для группы Managers'

    def handle(self, *args, **options):
        # Создание или получение группы Managers
        managers, created = Group.objects.get_or_create(name='Managers')

        if created:
            self.stdout.write('Группа Managers создана')
        else:
            self.stdout.write('Группа Managers уже существует')

        # Добавление прав для модели Recipient
        recipient_perms = Permission.objects.filter(
            codename__in=['can_view_all_recipients']
        )
        managers.permissions.add(*recipient_perms)

        # Добавление прав для модели Message
        message_perms = Permission.objects.filter(
            codename__in=['can_view_all_messages']
        )
        managers.permissions.add(*message_perms)

        # Добавление прав для модели Mailing
        mailing_perms = Permission.objects.filter(
            codename__in=['can_view_all_mailings', 'can_deactivate_mailing']
        )
        managers.permissions.add(*mailing_perms)

        # Добавление прав для модели User
        user_perms = Permission.objects.filter(
            codename__in=['can_view_user_list', 'can_block_user', 'can_view_user_stats']
        )
        managers.permissions.add(*user_perms)

        # Стандартные права Django
        standard_perms = Permission.objects.filter(
            codename__in=['view_recipient', 'view_message', 'view_mailing', 'view_user']
        )
        managers.permissions.add(*standard_perms)

        self.stdout.write(
            self.style.SUCCESS('Права успешно назначены группе Managers')
        )

        # Создание тестового пользователя manager
        user, created = User.objects.get_or_create(
            username='manager',
            defaults={
                'email': 'manager@example.com',
                'password': 'manager123',
                'is_staff': True,
            }
        )

        if created:
            user.groups.add(managers)
            self.stdout.write(
                self.style.SUCCESS('Создан тестовый менеджер: username: manager, password: manager123')
            )
        else:
            self.stdout.write(self.style.WARNING('Пользователь manager уже существует'))
