from django.contrib import admin

from .models import AuditEvent, AuditSession


@admin.register(AuditSession)
class AuditSessionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "source",
        "login_at",
        "logout_at",
        "last_seen_at",
        "login_ip",
        "last_ip",
        "last_method",
        "last_path",
        "last_status_code",
    )
    search_fields = ("user__email", "user__user_name", "user__document_number", "access_jti", "refresh_jti")
    list_filter = ("source", "logout_at")
    ordering = ("-login_at",)


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "event_type", "at", "ip", "method", "path", "status_code", "view_name")
    search_fields = ("user__email", "user__user_name", "path", "view_name")
    list_filter = ("event_type",)
    ordering = ("-at",)

