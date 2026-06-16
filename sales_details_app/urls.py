from django.urls import path
from . import views

urlpatterns = [
    path('', views.sales_details, name='sales_details'),   # Main dashboard
]