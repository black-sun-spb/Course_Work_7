from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.conf import settings

from .forms import UserRegisterForm, ProfileForm
from .models import CustomUser


# --- Регистрация пользователя ---
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # до активации по email
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Отправка письма активации
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            activation_link = request.build_absolute_uri(f'/users/activate/{uid}/{token}/')

            message = render_to_string('users/activation_email.html', {
                'activation_link': activation_link,
                'user': user,
            })

            send_mail(
                subject='Активация аккаунта',
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            messages.success(request, 'Регистрация прошла успешно! Проверьте вашу почту для активации.')
            return redirect('users:login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


# --- Активация пользователя по ссылке ---
def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Аккаунт успешно активирован! Теперь можно войти.')
        return redirect('users:login')
    else:
        messages.error(request, 'Ссылка активации недействительна!')
        return redirect('users:register')


# --- Авторизация ---
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')  # главная страница после входа
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})


# --- Выход ---
def logout_view(request):
    logout(request)
    return redirect('users:login')


# --- Просмотр профиля ---
@login_required
def profile_view(request):
    return render(request, 'users/profile.html', {'user': request.user})


# --- Редактирование профиля ---
@login_required
def profile_edit(request):
    user = get_object_or_404(CustomUser, pk=request.user.pk)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён успешно!')
            return redirect('users:profile')
    else:
        form = ProfileForm(instance=user)
    return render(request, 'users/profile_edit.html', {'form': form})
