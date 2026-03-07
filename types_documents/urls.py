from django.urls import path
from .views.document_type import document_types_list, document_type_create, document_type_delete, document_type_edit

urlpatterns = [
    # Rutas de types_documents
    path("document_types/", document_types_list, name="document_types_list"),
    path("document_types/create/", document_type_create, name="document_type_create"),
    path("document_types/<int:pk>/edit/", document_type_edit, name="document_type_edit"),
    path("document_types/<int:pk>/delete/", document_type_delete, name="document_type_delete"),
]