from __future__ import annotations

from django.utils import timezone
from rest_framework import serializers

from settings.timezone_utils import PeruDateTimeField
from ..models import AuditEvent


class AuditEventTableSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source="user.email", read_only=True)
    action = serializers.SerializerMethodField()
    ip = serializers.CharField(allow_null=True, required=False)
    detail = serializers.SerializerMethodField()
    datetime = PeruDateTimeField(source="at", read_only=True)
    active = serializers.SerializerMethodField()

    class Meta:
        model = AuditEvent
        fields = [
            "id",
            "user_id",
            "full_name",
            "email",
            "action",
            "ip",
            "detail",
            "datetime",
            "active",
        ]

    def get_full_name(self, obj: AuditEvent) -> str:
        u = obj.user
        try:
            if hasattr(u, "get_full_name"):
                return u.get_full_name() or ""
        except Exception:
            pass
        name = getattr(u, "name", "") or ""
        p = getattr(u, "paternal_lastname", "") or ""
        m = getattr(u, "maternal_lastname", "") or ""
        return " ".join(x for x in [name, p, m] if x).strip()

    def get_action(self, obj: AuditEvent) -> str:
        # 1) Si viene un label explícito en metadata
        if isinstance(obj.metadata, dict) and obj.metadata.get("action"):
            return str(obj.metadata["action"])

        # 2) Mapping básico por método+path para acciones frecuentes
        method = (obj.method or "").upper()
        path = obj.path or ""

        if method == "POST" and path.startswith("/api/employees/employee/create"):
            return "REGISTRAR_EMPLEADO"
        if method in ("PUT", "PATCH") and "/api/employees/employee/" in path and path.endswith("/edit/"):
            return "EDITAR_EMPLEADO"
        if method == "DELETE" and "/api/employees/employee/" in path and path.endswith("/delete/"):
            return "ELIMINAR_EMPLEADO"

        # 3) Login/Logout
        if obj.event_type == AuditEvent.Type.LOGIN:
            return "LOGIN"
        if obj.event_type == AuditEvent.Type.LOGOUT:
            return "LOGOUT"

        # 4) Fallback genérico
        if obj.view_name:
            return obj.view_name
        return f"{method} {path}".strip()

    def get_detail(self, obj: AuditEvent):
        """
        Devuelve el detalle relevante de la acción (metadata).
        """
        if isinstance(obj.metadata, dict) and obj.metadata:
            # evitar mandar payloads gigantes
            trimmed = dict(obj.metadata)
            if "request_body" in trimmed and isinstance(trimmed["request_body"], dict):
                body = trimmed["request_body"]
                # limitar llaves
                allowed = ["email", "user_id", "id", "document_number", "name"]
                trimmed["request_body"] = {k: body.get(k) for k in allowed if k in body}
            return trimmed
        return None

    def get_active(self, obj: AuditEvent) -> bool:
        if not obj.session:
            return False
        try:
            return obj.session.is_active(now=timezone.now())
        except Exception:
            return False

