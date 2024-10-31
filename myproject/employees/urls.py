# employees/urls.py
from django.urls import path
from .views import get_employees, create_employee, filter_by_designations, filter_by_gender, filter_by_age

urlpatterns = [
    path('getEmployees/', get_employees),
    path('addEmployees/', create_employee),
    path('filterDesignation/', filter_by_designations),
    path('filterGender/', filter_by_gender),
    path('filterAge/', filter_by_age),
]
