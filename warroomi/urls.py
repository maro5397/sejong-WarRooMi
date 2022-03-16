from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('warroombot/', include('warroombot.urls')),
    path('admin/', admin.site.urls),
]
