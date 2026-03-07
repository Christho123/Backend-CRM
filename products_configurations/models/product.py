from django.db import models
from django.utils import timezone
from .category import Category
from .supplier import Supplier
from .brand import Brand

class Product(models.Model):
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

    model = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        verbose_name="Modelo"
    )

    unit_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Precio Unitario"
    )

    sales_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Precio Venta"
    )

    stock = models.IntegerField(
        default=0,
        blank=True,
        null=True,
        verbose_name="Stock"
    )

    discount = models.DecimalField(
        default=0.00,
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Descuento"
    )

    photo = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        verbose_name="Foto"
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Categoria"
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Proveedor"
    )

    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Marca"
    )

    state = models.BooleanField(
        default=True,
        verbose_name="Estado"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "products"
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['name']

    def get_photo_url(self):
        """Retorna la URL de la foto si existe, None si no hay foto"""
        if self.photo and hasattr(self.photo, 'url'):
            return self.photo.url
        return None