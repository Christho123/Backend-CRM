from django.urls import path

from .views.audit import AuditActionsTableView, UserAuditDetailView

app_name = "audits"

urlpatterns = [
    # GET general (tabla de movimientos)
    path("sessions/", AuditActionsTableView.as_view(), name="actions_table"),
    path("events/", AuditActionsTableView.as_view(), name="actions_table_events_alias"),
    path("users/<int:user_id>/", UserAuditDetailView.as_view(), name="user_detail"),
]

