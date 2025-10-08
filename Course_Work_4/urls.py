from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('clients/', include('clients.urls', namespace='clients')),
    path('messages_app/', include('messages_app.urls')),
    path('mailings/', include('mailings.urls', namespace='mailings')),
    path('users/', include('users.urls', namespace='users')),
]
