from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.apps import apps

class Command(BaseCommand):
    help = 'Создает группу "Менеджеры" и назначает необходимые права'

    def handle(self, *args, **kwargs):
        group, created = Group.objects.get_or_create(name='Managers')
        if created:
            self.stdout.write(self.style.SUCCESS('Группа "Менеджеры" создана'))
        else:
            self.stdout.write('Группа "Менеджеры" уже существует')

        # Добавляем права для всех моделей приложений clients, mailings и messages_app
        models_to_assign = [
            ('clients', 'recipient'),
            ('mailings', 'mailing'),
            ('mailings', 'mailingattempt'),
            ('messages_app', 'message'),
        ]

        for app_label, model_name in models_to_assign:
            model = apps.get_model(app_label, model_name)
            perms = Permission.objects.filter(content_type__app_label=app_label, content_type__model=model_name)
            group.permissions.add(*perms)

        self.stdout.write(self.style.SUCCESS('Права успешно назначены группе "Менеджеры"'))
