from django.urls import path
from .views.category import category_list, category_create, category_delete, category_edit, category_detail
from .views.supplier import supplier_list, supplier_create, supplier_delete, supplier_update, supplier_detail
from .views.brand import brand_list, brand_create, brand_update, brand_delete, brand_detail
from .views.product import (
    product_list, product_create, product_delete, product_update, product_detail,
    product_photo_upload, product_photo_update, product_photo_delete
)

urlpatterns = [
    # Category
    path("category/", category_list, name="category_list"),
    path("category/create/", category_create, name="category_create"),
    path("category/<int:pk>/edit/", category_edit, name="category_edit"),
    path("category/<int:pk>/delete/", category_delete, name="category_delete"),
    path("category/<int:pk>/", category_detail, name="category_detail"),

    # Proveedor
    path("supplier/", supplier_list, name="supplier_list"),
    path("supplier/create/", supplier_create, name="supplier_create"),
    path("supplier/<int:pk>/edit/", supplier_update, name="supplier_update"),
    path("supplier/<int:pk>/delete/", supplier_delete, name="supplier_delete"),
    path("supplier/<int:pk>/", supplier_detail, name="supplier_detail"),
    
    # Marca
    path("brand/", brand_list, name="brand_list"),
    path("brand/create/", brand_create, name="brand_create"),
    path("brand/<int:pk>/edit/", brand_update, name="brand_update"),
    path("brand/<int:pk>/delete/", brand_delete, name="brand_delete"),
    path("brand/<int:pk>/", brand_detail, name="brand_detail"),

    # Producto
    path("product/", product_list, name="product_list"),
    path("product/create/", product_create, name="product_create"),
    path("product/<int:pk>/edit/", product_update, name="product_update"),
    path("product/<int:pk>/delete/", product_delete, name="product_delete"),
    path("product/<int:pk>/", product_detail, name="product_detail"),
    # Rutas de fotos de empleados
    path("product/<int:pk>/photo/", product_photo_upload, name="product_photo_upload"),
    path("product/<int:pk>/photo/edit/", product_photo_update, name="product_photo_update"),
    path("product/<int:pk>/photo/delete/", product_photo_delete, name="product_photo_delete"),
]