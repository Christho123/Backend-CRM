from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class AuditEvent(models.Model):
    class Type(models.TextChoices):
        LOGIN = "LOGIN", "Login"
        LOGOUT = "LOGOUT", "Logout"
        REQUEST = "REQUEST", "Request"

    session = models.ForeignKey(
        "audits.AuditSession",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="audit_events",
    )

    event_type = models.CharField(max_length=16, choices=Type.choices, db_index=True)
    at = models.DateTimeField(default=timezone.now, db_index=True)

    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    method = models.CharField(max_length=16, null=True, blank=True)
    path = models.CharField(max_length=512, null=True, blank=True)
    view_name = models.CharField(max_length=255, null=True, blank=True)
    status_code = models.PositiveSmallIntegerField(null=True, blank=True)

    metadata = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = "audit_events"
        indexes = [
            models.Index(fields=["user", "-at"]),
            models.Index(fields=["session", "-at"]),
            models.Index(fields=["event_type", "-at"]),
        ]

    def __str__(self) -> str:
        return f"AuditEvent(user_id={self.user_id}, type={self.event_type}, at={self.at})"

