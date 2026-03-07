from rest_framework import serializers
from ..models import Brand

class BrandSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)
    
    class Meta:
        model = Brand
        fields = ["id", "name", "description", "country", "country_name", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
