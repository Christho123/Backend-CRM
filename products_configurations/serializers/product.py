from rest_framework import serializers
from ..models import Product
from datetime import date
from ..serializers import CategorySerializer, SupplierSerializer, BrandSerializer
from ..models import Category, Supplier, Brand


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    supplier = SupplierSerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    photo_url = serializers.SerializerMethodField()

    category_name = serializers.CharField(source='category.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)

    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )
    supplier_id = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(),
        source='supplier',
        write_only=True
    )
    brand_id = serializers.PrimaryKeyRelatedField(
        queryset=Brand.objects.all(),
        source='brand',
        write_only=True
    )

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'model', 'unit_price', 'sales_price',
            'stock', 'discount', 'photo_url', 'category', 'category_id', 'category_name',
            'supplier', 'supplier_id', 'supplier_name', 'brand', 'brand_id', 'brand_name',
            'state', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_photo_url(self, obj):
        """Retorna la URL de la foto del producto"""
        return obj.get_photo_url()

    def validate_stock(self, value):
        """Verifica que el stock no sea negativo"""
        if value < 0:
            raise serializers.ValidationError("El stock no puede ser negativo.")
        return value

    def validate_sales_price(self, value):
        """Verifica que el precio de venta no sea negativo"""
        if value < 0:
            raise serializers.ValidationError("El precio de venta no puede ser negativo.")
        return value

    def validate_unit_price(self, value):
        if value < 0:
            raise serializers.ValidationError("El precio unitario no puede ser negativo.")
        return value

    def validate_discount(self, value):
        # Si el valor es None, lo tratamos como 0 para la validación
        if value is None:
            value = 0
        if not 0 <= value <= 100:
            raise serializers.ValidationError("El descuento debe estar entre 0 y 100%.")
        return value

    def validate(self, data):
        unit_price = data.get('unit_price', getattr(self.instance, 'unit_price', None))
        sales_price = data.get('sales_price', getattr(self.instance, 'sales_price', None))

        # Convertir a Decimal si no son None, o usar 0 para la comparación si son None
        unit_price_for_comparison = unit_price if unit_price is not None else 0
        sales_price_for_comparison = sales_price if sales_price is not None else 0

        if sales_price_for_comparison < unit_price_for_comparison:
            raise serializers.ValidationError("El precio de venta no puede ser menor que el precio unitario.")
        return data

    def create(self, validated_data):
        """Override create para asegurar que se carguen las relaciones"""
        product = super().create(validated_data)
        # Recargar con select_related para obtener las relaciones
        return Product.objects.select_related('category', 'supplier', 'brand').get(pk=product.pk)
