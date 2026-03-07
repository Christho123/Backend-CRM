from django.db import models
from django.utils import timezone
from ubi_geo.models import Region, Province, District

class Supplier(models.Model):
    ruc = models.CharField(
        max_length=255,
        blank=True, 
        null=True,
        unique=True,
        verbose_name="RUC"
    )
    
    company_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Razon Social"
    )

    business_name = models.CharField(
        max_length=255,
        blank=True, 
        null=True,
        verbose_name="Nombre Comercial del Proveedor"
    )

    representative = models.CharField(
        max_length=255,
        blank=True, 
        null=True,
        verbose_name="Nombre del Representante"
    )

    phone = models.CharField(
        max_length=15,
        blank=True, 
        null=True,
        verbose_name="Telefono de Contacto"
    )

    email = models.EmailField(
        max_length=255,
        unique=True,
        blank=True, 
        null=True,
        verbose_name="Email de Contacto"
    )

    address = models.CharField(
        max_length=255,
        blank=True, 
        null=True,
        verbose_name="Direccion de la Empresa"
    )

    account_number = models.CharField(
        max_length=100,
        unique=True,
        blank=True, 
        null=True,
        verbose_name="Numero de Cuenta de la Empresa"
    )

    region = models.ForeignKey(
        Region, 
        on_delete=models.CASCADE,
        blank=True, 
        null=True,
        verbose_name="Región"
        )

    province = models.ForeignKey(
        Province, 
        on_delete=models.CASCADE,
        blank=True, 
        null=True,
        verbose_name="Provincia")

    district = models.ForeignKey(
        District, 
        on_delete=models.CASCADE,
        blank=True, 
        null=True,
        verbose_name="Distrito"
        )

    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    def __str__(self):
        return self.company_name

    class Meta:
        db_table = "supplier"
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['company_name', 'ruc', 'representative', 'business_name']
