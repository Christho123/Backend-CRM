from __future__ import annotations

from typing import Any, Dict

from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from settings.timezone_utils import to_peru_iso
from ..services import AnalyticsService


class AnalyticsSummaryView(APIView):
    """
    Resumen general:
    - empleados totales
    - usuarios totales
    - clicks totales
    - clicks en products_configurations
    """

    permission_classes = [IsAdminUser]

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        data = AnalyticsService.get_summary()
        return Response(data)


class BaseTimeSeriesView(APIView):
    """
    Vista base para endpoints de series de tiempo.
    """

    permission_classes = [IsAdminUser]

    DEFAULT_PERIODS = {
        "day": 30,
        "week": 12,
        "month": 12,
    }

    def _parse_common_params(self, request: Request) -> Dict[str, Any]:
        granularity = request.query_params.get("granularity", "day").lower()
        if granularity not in ("day", "week", "month"):
            return {"error": "granularity debe ser 'day', 'week' o 'month'."}

        periods_param = request.query_params.get("periods")
        if periods_param is not None:
            try:
                periods = max(1, int(periods_param))
            except ValueError:
                return {"error": "periods debe ser un entero positivo."}
        else:
            periods = self.DEFAULT_PERIODS[granularity]

        return {
            "granularity": granularity,
            "periods": periods,
        }


class ClicksTimeSeriesView(BaseTimeSeriesView):
    """
    Serie de tiempo de clicks (requests auditados).

    Query params:
    - granularity: day|week|month (default: day)
    - periods: número de periodos hacia atrás (opcional)
    - scope: all|products (default: all)
    """

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        base = self._parse_common_params(request)
        if "error" in base:
            return Response({"detail": base["error"]}, status=400)

        scope = request.query_params.get("scope", "all").lower()
        if scope not in ("all", "products"):
            return Response({"detail": "scope debe ser 'all' o 'products'."}, status=400)

        result = AnalyticsService.get_clicks_timeseries(
            granularity=base["granularity"],
            periods=base["periods"],
            scope=scope,  # type: ignore[arg-type]
        )

        payload = {
            "granularity": result.granularity,
            "start": to_peru_iso(result.start),
            "end": to_peru_iso(result.end),
            "scope": scope,
            "results": result.points,
        }
        return Response(payload)


class NewEmployeesTimeSeriesView(BaseTimeSeriesView):
    """
    Serie de tiempo de empleados nuevos.

    Query params:
    - granularity: day|week|month (default: day)
    - periods: número de periodos hacia atrás (opcional)
    """

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        base = self._parse_common_params(request)
        if "error" in base:
            return Response({"detail": base["error"]}, status=400)

        result = AnalyticsService.get_new_employees_timeseries(
            granularity=base["granularity"],
            periods=base["periods"],
        )

        payload = {
            "granularity": result.granularity,
            "start": to_peru_iso(result.start),
            "end": to_peru_iso(result.end),
            "results": result.points,
        }
        return Response(payload)


class NewUsersTimeSeriesView(BaseTimeSeriesView):
    """
    Serie de tiempo de usuarios nuevos.

    Query params:
    - granularity: day|week|month (default: day)
    - periods: número de periodos hacia atrás (opcional)
    """

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        base = self._parse_common_params(request)
        if "error" in base:
            return Response({"detail": base["error"]}, status=400)

        result = AnalyticsService.get_new_users_timeseries(
            granularity=base["granularity"],
            periods=base["periods"],
        )

        payload = {
            "granularity": result.granularity,
            "start": to_peru_iso(result.start),
            "end": to_peru_iso(result.end),
            "results": result.points,
        }
        return Response(payload)

