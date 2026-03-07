from __future__ import annotations

from typing import Any, Optional

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from ..models import AuditEvent, AuditSession

User = get_user_model()


class AuditService:
    @staticmethod
    def get_client_ip(request) -> str | None:
        """
        Intenta obtener la IP real (soporta proxies típicos).
        """
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            # puede venir como: "ip1, ip2, ip3"
            ip = xff.split(",")[0].strip()
            return ip or None
        return request.META.get("REMOTE_ADDR")

    @staticmethod
    def get_user_agent(request) -> str | None:
        ua = request.META.get("HTTP_USER_AGENT")
        return ua or None

    @staticmethod
    def _token_jti(token: Any) -> str | None:
        try:
            return str(token.get("jti")) if token.get("jti") else None
        except Exception:
            return None

    @staticmethod
    @transaction.atomic
    def open_login_session(*, request, user: User, refresh: RefreshToken, access: AccessToken) -> AuditSession:
        ip = AuditService.get_client_ip(request)
        ua = AuditService.get_user_agent(request)
        now = timezone.now()

        session = AuditSession.objects.create(
            user=user,
            source=AuditSession.Source.LOGIN,
            login_at=now,
            last_seen_at=now,
            login_ip=ip,
            last_ip=ip,
            user_agent=ua,
            login_path=getattr(request, "path", None),
            access_jti=AuditService._token_jti(access),
            refresh_jti=AuditService._token_jti(refresh),
            last_method="POST",
            last_path=getattr(request, "path", None),
            last_status_code=200,
            last_action_at=now,
        )

        AuditEvent.objects.create(
            session=session,
            user=user,
            event_type=AuditEvent.Type.LOGIN,
            at=now,
            ip=ip,
            user_agent=ua,
            method="POST",
            path=getattr(request, "path", None),
            metadata={
                "source": "login",
            },
        )

        return session

    @staticmethod
    @transaction.atomic
    def close_session_by_refresh(*, request, user: User, refresh_token_str: str, reason: str = "logout") -> AuditSession | None:
        """
        Cierra la sesión asociada al refresh token (si existe).
        """
        try:
            refresh = RefreshToken(refresh_token_str)
        except Exception:
            return None

        refresh_jti = AuditService._token_jti(refresh)
        if not refresh_jti:
            return None

        session = (
            AuditSession.objects.select_for_update()
            .filter(user=user, refresh_jti=refresh_jti)
            .order_by("-login_at")
            .first()
        )
        if not session:
            return None

        now = timezone.now()
        ip = AuditService.get_client_ip(request)
        ua = AuditService.get_user_agent(request)

        if not session.logout_at:
            session.logout_at = now
            session.ended_reason = reason
            session.last_seen_at = now
            if ip:
                session.last_ip = ip
            if ua and not session.user_agent:
                session.user_agent = ua
            session.last_method = "POST"
            session.last_path = getattr(request, "path", None)
            session.last_status_code = 200
            session.last_action_at = now
            session.save()

        AuditEvent.objects.create(
            session=session,
            user=user,
            event_type=AuditEvent.Type.LOGOUT,
            at=now,
            ip=ip,
            user_agent=ua,
            method="POST",
            path=getattr(request, "path", None),
            metadata={"reason": reason},
        )

        return session

    @staticmethod
    @transaction.atomic
    def touch_and_log_request(
        *,
        request,
        user: User,
        access_jti: str | None,
        status_code: int | None,
        view_name: str | None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        now = timezone.now()
        ip = AuditService.get_client_ip(request)
        ua = AuditService.get_user_agent(request)

        session: AuditSession | None = None
        if access_jti:
            session = (
                AuditSession.objects.select_for_update()
                .filter(user=user, access_jti=access_jti)
                .order_by("-login_at")
                .first()
            )

        if not session:
            # fallback: crear una sesión implícita para no perder tracking
            session = AuditSession.objects.create(
                user=user,
                source=AuditSession.Source.IMPLICIT,
                login_at=now,
                last_seen_at=now,
                login_ip=ip,
                last_ip=ip,
                user_agent=ua,
                login_path=None,
                access_jti=access_jti,
                refresh_jti=None,
                last_method=getattr(request, "method", None),
                last_path=getattr(request, "path", None),
                last_status_code=status_code,
                last_action_at=now,
            )

        session.last_seen_at = now
        if ip:
            session.last_ip = ip
        if ua and not session.user_agent:
            session.user_agent = ua
        session.last_method = getattr(request, "method", None)
        session.last_path = getattr(request, "path", None)
        session.last_status_code = status_code
        session.last_action_at = now
        session.save(update_fields=["last_seen_at", "last_ip", "user_agent", "last_method", "last_path", "last_status_code", "last_action_at", "updated_at"])

        AuditEvent.objects.create(
            session=session,
            user=user,
            event_type=AuditEvent.Type.REQUEST,
            at=now,
            ip=ip,
            user_agent=ua,
            method=getattr(request, "method", None),
            path=getattr(request, "path", None),
            view_name=view_name,
            status_code=status_code,
            metadata=metadata or None,
        )

