from django.db import models
from django.contrib.auth.models import User


class Recipient(models.Model):
    email = models.EmailField(unique=True)
    full_name = models.CharField("ФИО", max_length=255, blank=True)
    comment = models.TextField("Комментарий", blank=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipients',
        verbose_name="Владелец"
    )


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['full_name']
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"
        permissions = [
            ("can_manage_recipients", "Может управлять получателями"),
        ]


    def __str__(self):
        return f"{self.full_name} <{self.email}>"
