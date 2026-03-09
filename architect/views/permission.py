from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..serializers.permission import PermissionSerializer, RoleSerializer
from ..models.permission import Permission, Role
from ..pagination import ArchitectPageNumberPagination, get_paginated_dict


class PermissionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        permissions = Permission.objects.all()
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RoleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk is not None:
            try:
                role = Role.objects.get(pk=pk)
                serializer = RoleSerializer(role)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Role.DoesNotExist:
                return Response({"error": "Rol no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        qs = Role.objects.all()
        paginator = ArchitectPageNumberPagination()
        page = paginator.paginate_queryset(qs, request)
        if page is None:
            return Response({"roles": [], "count": 0, "next": None, "previous": None})
        serializer = RoleSerializer(page, many=True)
        return Response(get_paginated_dict(paginator, serializer.data, "roles"))

    def post(self, request):
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        try:
            role = Role.objects.get(pk=pk)
        except Role.DoesNotExist:
            return Response({"error": "Rol no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = RoleSerializer(role, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        try:
            role = Role.objects.get(pk=pk)
            role_name = role.name
            role_id = role.id
        except Role.DoesNotExist:
            return Response({"error": "Rol no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        role.delete()
        return Response({
            "message": f"Rol '{role_name}' eliminado exitosamente",
            "deleted_role": {
                "id": role_id,
                "name": role_name
            }
        }, status=status.HTTP_200_OK)
