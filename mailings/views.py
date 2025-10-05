import logging
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.contrib import messages

from .models import Mailing, MailingAttempt
from messages_app.models import Message
from clients.models import Recipient

logger = logging.getLogger(__name__)

# --- Проверка роли менеджера ---
def is_manager(user):
    return user.groups.filter(name='Managers').exists()


# --- CRUD рассылок ---
class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailings/mailing_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        if is_manager(self.request.user):
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=self.request.user)


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    fields = ['message', 'recipients', 'start_datetime', 'end_datetime']
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    fields = ['message', 'recipients', 'start_datetime', 'end_datetime']
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:list')

    def get_queryset(self):
        if is_manager(self.request.user):
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=self.request.user)


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = 'mailings/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailings:list')

    def get_queryset(self):
        if is_manager(self.request.user):
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=self.request.user)


# --- Отправка сообщений ---
def send_message(mailing: Mailing):
    """Создает и отправляет попытки рассылки всем получателям."""
    now = timezone.now()

    if mailing.start_datetime > now:
        return f"Рассылка ещё не началась. Начало: {mailing.start_datetime}"
    if mailing.end_datetime < now:
        return f"Рассылка уже завершена. Конец: {mailing.end_datetime}"

    recipients = mailing.recipients.all()
    for client in recipients:
        attempt = MailingAttempt.objects.create(
            mailing=mailing,
            recipient_email=client.email,
        )
        attempt.send_email()  # метод модели MailingAttempt

    mailing.status = 'started'
    mailing.save()
    return "Рассылка отправлена"


class MailingSendNowView(LoginRequiredMixin, View):
    """Отправка рассылки по кнопке 'Отправить'."""
    def get(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)

        if not is_manager(request.user) and mailing.owner != request.user:
            messages.error(request, "Нет доступа к этой рассылке")
            return redirect('mailings:list')

        msg = send_message(mailing)
        messages.info(request, msg)
        return redirect('mailings:list')


# --- Статистика и отчеты с кешированием ---
class MailingStatisticsView(LoginRequiredMixin, TemplateView):
    template_name = 'mailings/mailing_statistics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_key = f"mailings_stats_{self.request.user.id}"
        stats = cache.get(user_key)

        if not stats:
            mailings = Mailing.objects.all() if is_manager(self.request.user) else Mailing.objects.filter(owner=self.request.user)
            stats = {
                'total_mailings': mailings.count(),
                'active_mailings': mailings.filter(status='started').count(),
                'unique_recipients': Recipient.objects.filter(mailings__in=mailings).distinct().count(),
                'successful_attempts': MailingAttempt.objects.filter(mailing__in=mailings, status='success').count(),
                'failed_attempts': MailingAttempt.objects.filter(mailing__in=mailings, status='failed').count(),
            }
            cache.set(user_key, stats, 60 * 5)

        context.update(stats)
        context['total_sent_messages'] = context['successful_attempts']
        return context
