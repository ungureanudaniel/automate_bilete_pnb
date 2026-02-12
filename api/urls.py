# api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('ticket/create', views.create_ticket),
    path('device/heartbeat', views.heartbeat),
]