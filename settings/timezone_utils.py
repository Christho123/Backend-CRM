"""
Utilidades para devolver fecha/hora en zona horaria de Perú (America/Lima).
Usar en todos los endpoints que serialicen datetime a JSON.
"""
from django.utils import timezone
from rest_framework import serializers


def to_peru_iso(dt):
    """
    Convierte un datetime a hora de Perú y lo devuelve en formato ISO.
    Si dt es None, devuelve None.
    Requiere USE_TZ=True y TIME_ZONE='America/Lima' en settings.
    """
    if dt is None:
        return None
    if timezone.is_naive(dt):
        return dt.isoformat()
    return timezone.localtime(dt).isoformat()


class PeruDateTimeField(serializers.DateTimeField):
    """Campo DateTime que serializa siempre en hora de Perú (America/Lima)."""
    def to_representation(self, value):
        return to_peru_iso(value)
