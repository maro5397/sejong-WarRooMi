from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('api/', include('warroombot.urls')),
    path('webhook/', include('googlewebhook.urls')),
    path('admin/', admin.site.urls),
]
