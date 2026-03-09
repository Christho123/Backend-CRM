from __future__ import annotations

from rest_framework.pagination import PageNumberPagination


def get_paginated_dict(paginator, data, results_key="results"):
    """Devuelve dict con count, next, previous y la lista bajo results_key."""
    response = paginator.get_paginated_response(data)
    d = dict(response.data)
    if "results" in d:
        d[results_key] = d.pop("results")
    return d


class EmployeePageNumberPagination(PageNumberPagination):
    """
    Paginación para endpoints de empleados.
    Tamaño de página por query param: page_size (solo 10, 20 o 50).
    """
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 50

    def get_page_size(self, request):
        allowed = (10, 20, 50)
        try:
            size = int(request.query_params.get(self.page_size_query_param, self.page_size))
            if size in allowed:
                return size
        except (TypeError, ValueError):
            pass
        return self.page_size
