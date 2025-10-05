from django.db import models
from django.utils import timezone
from messages_app.models import Message
from clients.models import Recipient
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User


class Mailing(models.Model):
    STATUS_CHOICES = [
        ('created', 'Создана'),
        ('started', 'Запущена'),
        ('finished', 'Завершена'),
    ]

    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    recipients = models.ManyToManyField(Recipient, related_name='mailings')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='created')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mailings')

    def save(self, *args, **kwargs):
        now = timezone.now()
        if self.end_datetime < now:
            self.status = 'finished'
        elif self.start_datetime <= now <= self.end_datetime:
            self.status = 'started'
        else:
            self.status = 'created'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.message} ({self.get_status_display()})'

    class Meta:
        permissions = [
            ("can_manage_mailings", "Может управлять рассылками"),
        ]
        ordering = ['-start_datetime']


class MailingAttempt(models.Model):
    STATUS_CHOICES = [
        ('success', 'Успешно'),
        ('failed', 'Не успешно'),
    ]

    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name='attempts')
    recipient_email = models.EmailField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='failed')
    server_response = models.TextField(blank=True)
    attempted_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.mailing} -> {self.recipient_email} ({self.get_status_display()})'

    def send_email(self):
        try:
            send_mail(
                subject=self.mailing.message.subject,
                message=self.mailing.message.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.recipient_email],
                fail_silently=False,
            )
            self.status = 'success'
            self.server_response = 'Сообщение отправлено успешно'
        except Exception as e:
            self.status = 'failed'
            self.server_response = str(e)
        finally:
            self.attempted_at = timezone.now()
            self.save()

    class Meta:
        permissions = [
            ("can_manage_attempts", "Может управлять попытками рассылки"),
        ]
        ordering = ['-attempted_at']
