from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from .models import Recipient
from .forms import RecipientForm

# --- Проверка роли менеджера ---
def is_manager(user):
    return user.groups.filter(name='Managers').exists()


@login_required
@cache_page(60 * 5)  # кешируем список получателей на 5 минут
def recipient_list(request):
    """Список получателей"""
    recipients = Recipient.objects.all() if is_manager(request.user) else Recipient.objects.filter(owner=request.user)
    return render(request, 'clients/recipient_list.html', {'recipients': recipients})


@login_required
def recipient_create(request):
    """Создание нового получателя"""
    if request.method == 'POST':
        form = RecipientForm(request.POST)
        if form.is_valid():
            recipient = form.save(commit=False)
            recipient.owner = request.user
            recipient.save()
            form.save_m2m()
            # Очистка кеша списка после добавления нового получателя
            from django.core.cache import cache
            cache.clear()
            return redirect('clients:list')
    else:
        form = RecipientForm()
    return render(request, 'clients/recipient_form.html', {'form': form})


@login_required
def recipient_update(request, pk):
    """Редактирование получателя"""
    recipient = get_object_or_404(Recipient, pk=pk)
    if not is_manager(request.user) and recipient.owner != request.user:
        return redirect('clients:list')

    if request.method == 'POST':
        form = RecipientForm(request.POST, instance=recipient)
        if form.is_valid():
            form.save()
            # Очистка кеша после изменения
            from django.core.cache import cache
            cache.clear()
            return redirect('clients:list')
    else:
        form = RecipientForm(instance=recipient)

    return render(request, 'clients/recipient_form.html', {'form': form})


@login_required
def recipient_delete(request, pk):
    """Удаление получателя"""
    recipient = get_object_or_404(Recipient, pk=pk)
    if not is_manager(request.user) and recipient.owner != request.user:
        return redirect('clients:list')

    if request.method == 'POST':
        recipient.delete()
        # Очистка кеша после удаления
        from django.core.cache import cache
        cache.clear()
        return redirect('clients:list')

    return render(request, 'clients/recipient_confirm_delete.html', {'recipient': recipient})
