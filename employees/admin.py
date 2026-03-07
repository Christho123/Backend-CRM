from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models.employee import Employees


@admin.register(Employees)
class EmployeesAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'get_full_name_display',
        'document_type',
        'document_number',
        'email',
        'phone',
        'get_location_display',
        'rol',
        'salary',
        'is_active_display',
        'created_at',
    ]
    
    list_filter = [
        'document_type',
        'rol',
        'gender',
        'region',
        'province',
        'district',
        'created_at',
        'updated_at',
    ]
    
    search_fields = [
        'name',
        'last_name_paternal',
        'last_name_maternal',
        'document_number',
        'email',
        'phone',
    ]
    
    list_per_page = 25
    list_max_show_all = 100
    
    fieldsets = (
        ('Información Personal', {
            'fields': (
                'name',
                'last_name_paternal',
                'last_name_maternal',
                'document_type',
                'document_number',
                'birth_date',
                'gender',
            )
        }),
        ('Información de Contacto', {
            'fields': (
                'email',
                'phone',
                'address',
            )
        }),
        ('Ubicación', {
            'fields': (
                'region',
                'province',
                'district',
            )
        }),
        ('Información Laboral', {
            'fields': (
                'rol',
                'salary',
            )
        }),
        ('Foto de Perfil', {
            'fields': (
                'photo',
            ),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = [
        'created_at',
        'updated_at',
    ]
    
    autocomplete_fields = [
        'document_type',
        'rol',
        'region',
        'province',
        'district',
    ]
    
    raw_id_fields = [
        'region',
        'province',
        'district',
    ]
    
    date_hierarchy = 'created_at'
    
    ordering = ['-created_at']
    
    def get_full_name_display(self, obj):
        """Muestra el nombre completo del empleado"""
        if obj.name and obj.last_name_paternal:
            return f"{obj.name} {obj.last_name_paternal} {obj.last_name_maternal or ''}".strip()
        return "Sin nombre completo"
    get_full_name_display.short_description = "Nombre Completo"
    get_full_name_display.admin_order_field = 'name'
    
    def get_location_display(self, obj):
        """Muestra la ubicación del empleado"""
        location_parts = []
        if obj.region:
            location_parts.append(obj.region.name)
        if obj.province:
            location_parts.append(obj.province.name)
        if obj.district:
            location_parts.append(obj.district.name)
        
        if location_parts:
            return " → ".join(location_parts)
        return "Sin ubicación"
    get_location_display.short_description = "Ubicación"
    get_location_display.admin_order_field = 'region__name'
    
    def is_active_display(self, obj):
        """Muestra el estado del empleado con colores"""
        # Asumiendo que tienes un campo is_active, si no lo tienes, puedes usar otro campo
        if hasattr(obj, 'is_active'):
            if obj.is_active:
                return format_html(
                    '<span style="color: green; font-weight: bold;">✓ Activo</span>'
                )
            else:
                return format_html(
                    '<span style="color: red; font-weight: bold;">✗ Inactivo</span>'
                )
        else:
            return format_html(
                '<span style="color: blue;">-</span>'
            )
    is_active_display.short_description = "Estado"
    
    def get_queryset(self, request):
        """Optimiza las consultas con select_related"""
        queryset = super().get_queryset(request)
        return queryset.select_related(
            'document_type',
            'rol',
            'region',
            'province',
            'district'
        )
    
    def save_model(self, request, obj, form, change):
        """Personaliza el guardado del modelo"""
        if not change:  # Si es un nuevo empleado
            # Aquí puedes agregar lógica adicional para nuevos empleados
            pass
        
        super().save_model(request, obj, form, change)
    


# Configuración adicional para el admin
admin.site.site_header = "MyCell - Administración"
admin.site.site_title = "MyCell Admin"
admin.site.index_title = "Panel de Administración"
