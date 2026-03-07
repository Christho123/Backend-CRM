from __future__ import annotations

import re
from typing import Optional

from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication

from ..services import AuditService


class RequestAuditMiddleware(MiddlewareMixin):
    """
    Registra "movimientos" (requests) de usuarios autenticados:
    - actualiza last_seen_* en AuditSession
    - crea AuditEvent tipo REQUEST con path/method/status_code
    """

    SKIP_PATHS = [
        r"^/admin/",
        r"^/health/?$",
        r"^/static/",
        r"^/media/",
        r"^/api/audits/",  # evita recursión
        r"^/api/architect/auth/login/?$",
        r"^/api/architect/auth/logout/?$",
        r"^/api/architect/auth/register/?$",
    ]

    def _should_skip(self, request) -> bool:
        if request.method == "OPTIONS":
            return True

        path = getattr(request, "path", "") or ""
        for pattern in self.SKIP_PATHS:
            if re.match(pattern, path):
                return True

        if not path.startswith("/api/"):
            return True

        return False

    def process_request(self, request):
        if self._should_skip(request):
            return None

        user = None
        access_jti: Optional[str] = None

        # 1) Si ya viene autenticado (Session/Basic), usarlo
        try:
            if hasattr(request, "user") and request.user and request.user.is_authenticated:
                user = request.user
        except Exception:
            user = None

        # 2) Si no, intentar JWT (DRF autentica en la vista, así que aquí lo hacemos nosotros)
        if not user:
            try:
                auth_tuple = JWTAuthentication().authenticate(request)
                if auth_tuple:
                    user, validated_token = auth_tuple
                    access_jti = str(validated_token.get("jti")) if validated_token.get("jti") else None
            except Exception:
                user = None
                access_jti = None

        request._audit_user = user
        request._audit_access_jti = access_jti
        return None

    def process_response(self, request, response):
        try:
            if self._should_skip(request):
                return response

            user = getattr(request, "_audit_user", None)
            if not user or not getattr(user, "is_authenticated", False):
                return response

            access_jti = getattr(request, "_audit_access_jti", None)

            view_name = None
            try:
                match = getattr(request, "resolver_match", None)
                if match:
                    view_name = match.view_name
            except Exception:
                view_name = None

            AuditService.touch_and_log_request(
                request=request,
                user=user,
                access_jti=access_jti,
                status_code=getattr(response, "status_code", None),
                view_name=view_name,
                metadata=getattr(request, "_audit_metadata", None),
            )
        except Exception:
            # No bloquear el request por auditoría
            pass

        return response

