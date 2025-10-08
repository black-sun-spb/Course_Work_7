from django.db import models


class Message(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()

    def __str__(self):
        return self.subject

    class Meta:
        permissions = [
            ("can_manage_messages", "Может управлять сообщениями"),
        ]
        ordering = ['subject']  # сортировка по теме сообщения

