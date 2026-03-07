from rest_framework import serializers

from ..models import AuditEvent


class AuditEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditEvent
        fields = [
            "id",
            "event_type",
            "at",
            "ip",
            "user_agent",
            "method",
            "path",
            "view_name",
            "status_code",
            "metadata",
            "session",
        ]

