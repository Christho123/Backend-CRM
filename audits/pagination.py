from __future__ import annotations

from rest_framework.pagination import PageNumberPagination


class AuditPageNumberPagination(PageNumberPagination):
    """
    Paginación para endpoints de auditoría.
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
