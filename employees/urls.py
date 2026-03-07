from django.urls import path
from .views.employee import (
    employee_list, employee_create, employee_delete, employee_update, employee_detail,
    employee_photo_upload, employee_photo_update, employee_photo_delete
)

urlpatterns = [
    # Rutas de empleados
    path("employee/", employee_list, name="employee_list"),
    path("employee/create/", employee_create, name="employee_create"),
    path("employee/<int:pk>/", employee_detail, name="employee_detail"),
    path("employee/<int:pk>/edit/", employee_update, name="employee_update"),
    path("employee/<int:pk>/delete/", employee_delete, name="employee_delete"),
    
    # Rutas de fotos de empleados
    path("employee/<int:pk>/photo/", employee_photo_upload, name="employee_photo_upload"),
    path("employee/<int:pk>/photo/edit/", employee_photo_update, name="employee_photo_update"),
    path("employee/<int:pk>/photo/delete/", employee_photo_delete, name="employee_photo_delete"),
]