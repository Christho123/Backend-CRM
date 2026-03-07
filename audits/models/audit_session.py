from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class AuditSession(models.Model):
    class Source(models.TextChoices):
        LOGIN = "LOGIN", "Login"
        IMPLICIT = "IMPLICIT", "Implicit"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="audit_sessions",
    )

    source = models.CharField(max_length=16, choices=Source.choices, default=Source.LOGIN)

    login_at = models.DateTimeField(default=timezone.now)
    logout_at = models.DateTimeField(null=True, blank=True)
    last_seen_at = models.DateTimeField(null=True, blank=True)

    login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    access_jti = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    refresh_jti = models.CharField(max_length=255, null=True, blank=True, db_index=True)

    login_path = models.CharField(max_length=512, null=True, blank=True)

    last_method = models.CharField(max_length=16, null=True, blank=True)
    last_path = models.CharField(max_length=512, null=True, blank=True)
    last_status_code = models.PositiveSmallIntegerField(null=True, blank=True)
    last_action_at = models.DateTimeField(null=True, blank=True)

    ended_reason = models.CharField(max_length=64, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "audit_sessions"
        indexes = [
            models.Index(fields=["user", "-login_at"]),
            models.Index(fields=["logout_at"]),
            models.Index(fields=["last_seen_at"]),
        ]

    def __str__(self) -> str:
        return f"AuditSession(user_id={self.user_id}, login_at={self.login_at}, logout_at={self.logout_at})"

    @property
    def is_logged_out(self) -> bool:
        return self.logout_at is not None

    def is_active(self, now: timezone.datetime | None = None) -> bool:
        """
        Aproximación de "sigue dentro del sistema":
        - No hay logout
        - last_seen_at dentro de una ventana (AUDIT_ACTIVE_MINUTES, default 15)
        """
        if self.logout_at:
            return False

        now = now or timezone.now()
        minutes = getattr(settings, "AUDIT_ACTIVE_MINUTES", 15)
        window = timedelta(minutes=int(minutes))

        if not self.last_seen_at:
            return False

        return (now - self.last_seen_at) <= window

