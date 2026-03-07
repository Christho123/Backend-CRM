from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Literal, List, Dict, Any

from django.contrib.auth import get_user_model
from django.db.models import Count, QuerySet
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from django.utils import timezone

from audits.models import AuditEvent
from employees.models.employee import Employees


User = get_user_model()

Granularity = Literal["day", "week", "month"]


@dataclass
class TimeSeriesResult:
    granularity: Granularity
    start: timezone.datetime
    end: timezone.datetime
    points: List[Dict[str, Any]]


class AnalyticsService:
    @staticmethod
    def _get_range(granularity: Granularity, periods: int) -> tuple[timezone.datetime, timezone.datetime]:
        """
        Calcula el rango de tiempo hacia atrás a partir de ahora para N periodos.
        """
        now = timezone.now()

        if granularity == "day":
            delta = timedelta(days=periods)
        elif granularity == "week":
            delta = timedelta(weeks=periods)
        else:  # "month"
            # Aproximación: 30 días por mes
            delta = timedelta(days=30 * periods)

        start = now - delta
        return start, now

    @staticmethod
    def _apply_trunc(qs: QuerySet, field: str, granularity: Granularity) -> QuerySet:
        if granularity == "day":
            return qs.annotate(period=TruncDate(field))
        if granularity == "week":
            return qs.annotate(period=TruncWeek(field))
        return qs.annotate(period=TruncMonth(field))

    # --------- RESUMEN ---------
    @staticmethod
    def get_summary() -> Dict[str, Any]:
        """
        Resumen simple para cabeceras de dashboards.
        """
        total_employees = Employees.objects.count()
        total_users = User.objects.filter(deleted_at__isnull=True).count()
        total_clicks = AuditEvent.objects.filter(event_type=AuditEvent.Type.REQUEST).count()
        total_clicks_products = AuditEvent.objects.filter(
            event_type=AuditEvent.Type.REQUEST,
            path__startswith="/api/products_configurations/",
        ).count()

        return {
            "employees_total": total_employees,
            "users_total": total_users,
            "clicks_total": total_clicks,
            "clicks_products_total": total_clicks_products,
        }

    # --------- CLICKS ---------
    @staticmethod
    def get_clicks_timeseries(
        *,
        granularity: Granularity,
        periods: int,
        scope: Literal["all", "products"],
    ) -> TimeSeriesResult:
        start, end = AnalyticsService._get_range(granularity, periods)

        qs = AuditEvent.objects.filter(
            event_type=AuditEvent.Type.REQUEST,
            at__gte=start,
            at__lte=end,
            status_code__gte=200,
            status_code__lt=400,
        )

        if scope == "products":
            qs = qs.filter(path__startswith="/api/products_configurations/")

        qs = AnalyticsService._apply_trunc(qs, "at", granularity)
        qs = qs.values("period").order_by("period").annotate(count=Count("id"))

        points = [
            {
                "period": item["period"].date().isoformat() if hasattr(item["period"], "date") else item["period"].isoformat(),
                "count": item["count"],
            }
            for item in qs
        ]

        return TimeSeriesResult(
            granularity=granularity,
            start=start,
            end=end,
            points=points,
        )

    # --------- EMPLEADOS NUEVOS ---------
    @staticmethod
    def get_new_employees_timeseries(
        *,
        granularity: Granularity,
        periods: int,
    ) -> TimeSeriesResult:
        start, end = AnalyticsService._get_range(granularity, periods)

        qs = Employees.objects.filter(
            created_at__gte=start,
            created_at__lte=end,
        )
        qs = AnalyticsService._apply_trunc(qs, "created_at", granularity)
        qs = qs.values("period").order_by("period").annotate(count=Count("id"))

        points = [
            {
                "period": item["period"].date().isoformat() if hasattr(item["period"], "date") else item["period"].isoformat(),
                "count": item["count"],
            }
            for item in qs
        ]

        return TimeSeriesResult(
            granularity=granularity,
            start=start,
            end=end,
            points=points,
        )

    # --------- USUARIOS NUEVOS ---------
    @staticmethod
    def get_new_users_timeseries(
        *,
        granularity: Granularity,
        periods: int,
    ) -> TimeSeriesResult:
        start, end = AnalyticsService._get_range(granularity, periods)

        qs = User.objects.filter(
            created_at__gte=start,
            created_at__lte=end,
            deleted_at__isnull=True,
        )
        qs = AnalyticsService._apply_trunc(qs, "created_at", granularity)
        qs = qs.values("period").order_by("period").annotate(count=Count("id"))

        points = [
            {
                "period": item["period"].date().isoformat() if hasattr(item["period"], "date") else item["period"].isoformat(),
                "count": item["count"],
            }
            for item in qs
        ]

        return TimeSeriesResult(
            granularity=granularity,
            start=start,
            end=end,
            points=points,
        )

