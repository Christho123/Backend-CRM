# users_profiles/views/register.py
"""Registro público de usuarios (mismos datos que createsuperuser)."""

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers.user import PublicRegisterSerializer


class PublicRegisterView(APIView):
    """
    Registro público: cualquiera puede crear una cuenta sin estar autenticado.
    Campos: email, user_name, document_number, document_type (ID), password.
    """

    permission_classes = [AllowAny]
    serializer_class = PublicRegisterSerializer

    def post(self, request):
        serializer = PublicRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": "Usuario registrado correctamente.",
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "user_name": user.user_name,
                        "document_number": user.document_number,
                        "document_type_id": user.document_type_id,
                        "document_type": user.document_type.name if user.document_type else None,
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
