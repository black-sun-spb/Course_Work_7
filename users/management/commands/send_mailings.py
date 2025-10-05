from django.core.management.base import BaseCommand
from mailings.models import Mailing
from mailings.views import send_message

class Command(BaseCommand):
    help = 'Отправка активных рассылок'

    def handle(self, *args, **kwargs):
        active_mailings = Mailing.objects.filter(status='started')
        for mailing in active_mailings:
            recipients = mailing.recipients.all()
            send_message(mailing.message, recipients, mailing)
        self.stdout.write(self.style.SUCCESS('Все рассылки отправлены'))
