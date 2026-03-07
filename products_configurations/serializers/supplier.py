from rest_framework import serializers
from ..models import Supplier
import re
from datetime import date
from ubi_geo.models import Region, Province, District
from ubi_geo.serializers import RegionSerializer, ProvinceSerializer, DistrictSerializer

class SupplierSerializer(serializers.ModelSerializer):
    # Serializadores anidados para mostrar datos completos
    region = RegionSerializer(read_only=True)
    province = ProvinceSerializer(read_only=True)
    district = DistrictSerializer(read_only=True)
    
    # Campos de nombres para mostrar en lugar de IDs
    region_name = serializers.CharField(source='region.name', read_only=True)
    province_name = serializers.CharField(source='province.name', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)
    
    # Campos para escritura (crear/actualizar)
    region_id = serializers.PrimaryKeyRelatedField(
        queryset=Region.objects.all(), 
        source='region', 
        write_only=True,
        required=False,
        allow_null=True
    )
    province_id = serializers.PrimaryKeyRelatedField(
        queryset=Province.objects.all(), 
        source='province', 
        write_only=True,
        required=False,
        allow_null=True
    )
    district_id = serializers.PrimaryKeyRelatedField(
        queryset=District.objects.all(), 
        source='district', 
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Supplier
        fields = [
            'id', 'ruc','company_name', 'business_name', 'representative', 'phone',
            'email', 'address', 'account_number', 'region', 'region_name', 'province', 
            'province_name', 'district', 'district_name', 'created_at', 'updated_at',
            'region_id', 'province_id', 'district_id'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    def validate(self, attrs):
        """
        Asegura coherencia jerárquica:
        province debe pertenecer a region
        district debe pertenecer a province
        """
        region = attrs.get("region") or getattr(self.instance, "region", None)
        province = attrs.get("province") or getattr(self.instance, "province", None)
        district = attrs.get("district") or getattr(self.instance, "district", None)

        if province and region and province.region_id != region.id:
            raise serializers.ValidationError(
                "La provincia seleccionada no pertenece a la región."
            )
        if district and province and district.province_id != province.id:
            raise serializers.ValidationError(
                "El distrito seleccionado no pertenece a la provincia."
            )
        return attrs