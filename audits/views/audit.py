from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import AuditEvent, AuditSession
from ..pagination import AuditPageNumberPagination
from ..serializers import AuditEventSerializer, AuditEventTableSerializer
from users_profiles.serializers.user import UserSerializer as FullUserSerializer

User = get_user_model()


class AuditActionsTableView(generics.ListAPIView):
    """
    GET general: tabla de acciones (movimientos).

    Paginación: ?page=1&page_size=10|20|50 (por defecto 20).
    Filtros: user_id, active=true|false
    """

    permission_classes = [permissions.IsAdminUser]
    serializer_class = AuditEventTableSerializer
    pagination_class = AuditPageNumberPagination

    def get_queryset(self):
        # Más recientes primero: por fecha/hora descendente, luego por id descendente
        qs = AuditEvent.objects.select_related("user", "session").order_by("-at", "-id")

        user_id = self.request.query_params.get("user_id")
        if user_id:
            qs = qs.filter(user_id=user_id)

        active = self.request.query_params.get("active")
        if active is not None:
            active_bool = str(active).lower() in ("1", "true", "t", "yes", "y")
            if active_bool:
                qs = qs.filter(session__logout_at__isnull=True)
            else:
                qs = qs.filter(session__logout_at__isnull=False)

        return qs


class UserAuditDetailView(APIView):
    """
    GET específico: datos completos del usuario + acciones (movimientos).
    """

    permission_classes = [permissions.IsAdminUser]

    def get(self, request, user_id: int):
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"error": "Usuario no encontrado"}, status=404)

        events_limit = int(request.query_params.get("events_limit", 100))

        events_qs = AuditEvent.objects.select_related("session", "user").filter(user_id=user_id).order_by("-at")
        events = list(events_qs[: max(1, events_limit)])

        active = AuditSession.objects.filter(user_id=user_id, logout_at__isnull=True).exists()

        payload = {
            "user": FullUserSerializer(user, context={"request": request}).data,
            "active": active,
            "events": AuditEventTableSerializer(events, many=True).data,
        }

        return Response(payload)

