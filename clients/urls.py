from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    path('', views.recipient_list, name='list'),
    path('create/', views.recipient_create, name='create'),
    path('<int:pk>/update/', views.recipient_update, name='update'),
    path('<int:pk>/delete/', views.recipient_delete, name='delete'),
]
