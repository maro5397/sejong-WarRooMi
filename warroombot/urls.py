from django.urls import path, include
from . import views

urlpatterns = [
    path('keyboard/', views.keyboard),
    path('message/', views.answer),
]
