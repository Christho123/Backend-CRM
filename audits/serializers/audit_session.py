from django.utils import timezone
from rest_framework import serializers

from ..models import AuditSession


class AuditUserMiniSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    user_name = serializers.CharField(allow_null=True, required=False)
    document_number = serializers.CharField(allow_null=True, required=False)
    full_name = serializers.CharField(allow_blank=True, required=False)


class AuditSessionSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    active = serializers.SerializerMethodField()

    class Meta:
        model = AuditSession
        fields = [
            "id",
            "source",
            "user",
            "login_at",
            "logout_at",
            "last_seen_at",
            "login_ip",
            "last_ip",
            "user_agent",
            "login_path",
            "last_method",
            "last_path",
            "last_status_code",
            "last_action_at",
            "ended_reason",
            "active",
        ]

    def get_user(self, obj: AuditSession):
        u = obj.user
        full_name = ""
        try:
            if hasattr(u, "get_full_name"):
                full_name = u.get_full_name() or ""
        except Exception:
            full_name = ""

        return {
            "id": u.id,
            "email": getattr(u, "email", None),
            "user_name": getattr(u, "user_name", None),
            "document_number": getattr(u, "document_number", None),
            "full_name": full_name,
        }

    def get_active(self, obj: AuditSession) -> bool:
        return obj.is_active(now=timezone.now())

