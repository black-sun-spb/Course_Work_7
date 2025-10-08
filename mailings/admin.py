from django.contrib import admin
from .models import Mailing


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'status', 'start_datetime', 'end_datetime')
    list_filter = ('status',)
    search_fields = ('message__subject',)
