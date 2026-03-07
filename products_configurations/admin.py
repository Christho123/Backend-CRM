from django.contrib import admin
from .models.category import Category
from .models.supplier import Supplier
from .models.brand import Brand
from .models.product import Product

#Registrar el modelo en el admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name',)
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')

#Registrar el modelo en el admin
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('id', 'ruc','company_name', 'business_name', 'representative', 'phone',
            'email', 'address', 'account_number', 'region', 'province', 'district')
    search_fields = ('ruc', 'company_name', 'business_name', 'representative')
    ordering = ('company_name', 'ruc', 'representative', 'business_name')
    readonly_fields = ('created_at', 'updated_at')
    
#Registrar el modelo en el admin
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'country')
    search_fields = ('name', 'description', 'country__name')
    ordering = ['name']
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'model', 'unit_price', 'sales_price', 'stock',
        'discount', 'state', 'category', 'supplier', 'brand', 'created_at'
    )
    list_filter = ('state', 'category', 'brand', 'supplier')
    search_fields = ('name', 'model', 'category__name', 'brand__name', 'supplier__company_name')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Información general', {
            'fields': ('name', 'description', 'model', 'photo')
        }),
        ('Precios y stock', {
            'fields': ('unit_price', 'sales_price', 'discount', 'stock')
        }),
        ('Relaciones', {
            'fields': ('category', 'supplier', 'brand')
        }),
        ('Estado y fechas', {
            'fields': ('state', 'created_at', 'updated_at')
        }),
    )