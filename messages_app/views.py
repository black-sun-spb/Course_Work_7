import logging
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from .models import Message


logger = logging.getLogger(__name__)


# --- Проверка роли менеджера ---
def is_manager(user):
    return user.groups.filter(name='Managers').exists()


# --- CRUD сообщений ---
@method_decorator(cache_page(60 * 5), name='dispatch')  # кешируем список сообщений 5 минут
class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'messages_app/message_list.html'
    context_object_name = 'messages'

    def get_queryset(self):
        if is_manager(self.request.user):
            return Message.objects.all()
        return Message.objects.filter(owner=self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    fields = ['subject', 'body']
    template_name = 'messages_app/message_form.html'
    success_url = reverse_lazy('messages_app:list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Message
    fields = ['subject', 'body']
    template_name = 'messages_app/message_form.html'
    success_url = reverse_lazy('messages_app:list')

    def test_func(self):
        message = self.get_object()
        return is_manager(self.request.user) or message.owner == self.request.user


class MessageDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Message
    template_name = 'messages_app/message_confirm_delete.html'
    success_url = reverse_lazy('messages_app:list')

    def test_func(self):
        message = self.get_object()
        return is_manager(self.request.user) or message.owner == self.request.user
