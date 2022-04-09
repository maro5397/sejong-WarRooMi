from django.urls import path, include
from . import views


urlpatterns = [
    path('create/', views.create),
    path('delete/', views.delete),
    path('retrieve/', views.retrieve),
    path('getCalendar/', views.getCalendar),
]
