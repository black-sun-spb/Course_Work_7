from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Message(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_app')

    def __str__(self):
        return self.subject

    class Meta:
        permissions = [
            ("can_manage_messages", "Может управлять сообщениями"),
        ]
        ordering = ['subject']  # сортировка по теме сообщения
