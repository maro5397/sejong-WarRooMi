from django.urls import path, include
from . import views


urlpatterns = [
    path('googledrive/', views.googledrive),
]
