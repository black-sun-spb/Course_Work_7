import logging
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from .models import Mailing, MailingAttempt


logger = logging.getLogger(__name__)


def send_scheduled_mailings():
    """
    Автоматическая отправка всех рассылок, которые нужно отправить.
    """
    now = timezone.now()
    mailings = Mailing.objects.filter(
        status='created',
        start_datetime__lte=now,
        end_datetime__gte=now
    )

    for mailing in mailings:
        recipients = mailing.recipients.all()
        for recipient in recipients:
            try:
                send_mail(
                    subject=mailing.message.subject,
                    message=mailing.message.body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient.email],
                    fail_silently=False
                )
                MailingAttempt.objects.create(
                    mailing=mailing,
                    recipient_email=recipient.email,
                    status='success',
                    server_response='Сообщение успешно отправлено',
                    attempted_at=timezone.now()
                )
                logger.info(f"Сообщение '{mailing.message.subject}' отправлено {recipient.email}")
            except Exception as e:
                MailingAttempt.objects.create(
                    mailing=mailing,
                    recipient_email=recipient.email,
                    status='failed',
                    server_response=str(e),
                    attempted_at=timezone.now()
                )
                logger.error(f"Ошибка при отправке сообщения '{mailing.message.subject}' {recipient.email}: {str(e)}")

        # После отправки всех сообщений меняем статус рассылки
        mailing.status = 'started'
        mailing.save()


# Планировщик APScheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Запуск функции каждые 1 минуту
scheduler.add_job(
    send_scheduled_mailings,
    trigger=IntervalTrigger(minutes=1),
    id='send_scheduled_mailings',
    name='Авт. отправка рассылок каждую минуту',
    replace_existing=True
)

logger.info("Планировщик автоматической отправки рассылок запущен")
