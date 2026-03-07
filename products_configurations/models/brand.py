from django.db import models
from django.utils import timezone
from ubi_geo.models import Country

class Brand(models.Model):
    name = models.CharField(
        max_length=255,
        blank=True, 
        null=True,
        verbose_name="Nombre"
    )

    description = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Descripción"
    )

    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Pais de Origen"
    )

    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "brands"
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
        ordering = ['name']
