from rest_framework import serializers
from django.contrib.auth import get_user_model
from settings.timezone_utils import PeruDateTimeField

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    document_type_name = serializers.CharField(source='document_type.name', read_only=True)
    country_name = serializers.CharField(source='country.name', read_only=True)
    full_name = serializers.SerializerMethodField()
    photo_url_display = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True, required=False, min_length=8)

    last_session = PeruDateTimeField(read_only=True)
    email_verified_at = PeruDateTimeField(read_only=True)
    last_login = PeruDateTimeField(read_only=True)
    date_joined = PeruDateTimeField(read_only=True)
    created_at = PeruDateTimeField(read_only=True)
    updated_at = PeruDateTimeField(read_only=True)
    deleted_at = PeruDateTimeField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'document_type', 'document_type_name', 'document_number', 'photo_url', 'photo_url_display',
            'name', 'paternal_lastname', 'maternal_lastname', 'full_name', 'email', 'sex', 'phone', 'user_name',
            'password', 'password_change', 'last_session', 'account_statement', 'email_verified_at', 'country', 'country_name',
            'remember_token', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined',
            'created_at', 'updated_at', 'deleted_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'deleted_at', 'last_login', 'date_joined',
            'document_type_name', 'country_name', 'full_name', 'photo_url_display',
            'is_active', 'is_staff', 'is_superuser',  # Se asignan automáticamente en create(), no desde el cliente
        ]

    def create(self, validated_data):
        """Crea usuario con privilegios completos (is_staff, is_superuser) y contraseña hasheada."""
        password = validated_data.pop('password', None)
        user = User.objects.create_user(
            email=validated_data.pop('email'),
            password=password,
            is_staff=True,
            is_superuser=True,
            is_active=True,
            **validated_data
        )
        return user

    def update(self, instance, validated_data):
        """Actualiza usuario; si viene password, se hashea."""
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def get_full_name(self, obj):
        """Retorna el nombre completo concatenado."""
        parts = []
        if obj.name:
            parts.append(obj.name)
        if obj.paternal_lastname:
            parts.append(obj.paternal_lastname)
        if obj.maternal_lastname:
            parts.append(obj.maternal_lastname)
        return ' '.join(parts) if parts else ''
    
    def get_photo_url_display(self, obj):
        """Retorna la URL completa de la foto si existe."""
        if obj.photo_url:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.photo_url.url)
            return obj.photo_url.url
        return None