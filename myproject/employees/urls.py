# employees/urls.py
from django.urls import path
from .views import get_employees

urlpatterns = [
    path('getEmployees/', get_employees),
]
