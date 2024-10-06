# employees/urls.py
from django.urls import path
from .views import get_employees, create_employee

urlpatterns = [
    path('getEmployees/', get_employees),
    path('addEmployees/', create_employee),
]
