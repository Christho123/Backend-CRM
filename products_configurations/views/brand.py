import json
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from settings.timezone_utils import to_peru_iso
from ..models.brand import Brand
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication


def _json_body(request):
    try:
        return json.loads(request.body.decode() or "{}")
    except Exception:
        return {}

@csrf_exempt
@api_view(["GET"]) 
@authentication_classes([JWTAuthentication, SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def brand_list(request):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    qs = Brand.objects.select_related("country")
    data = []
    for b in qs:
        data.append({
            "id": b.id,
            "name": b.name,
            "description": b.description,
            "country": (
                {"id": b.country_id, "name": b.country.name}
                if b.country else None
            ),
            "created_at": to_peru_iso(b.created_at),
            "updated_at": to_peru_iso(b.updated_at)
        })
    return JsonResponse({"brands": data})

@csrf_exempt
@api_view(["POST"]) 
@authentication_classes([JWTAuthentication, SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def brand_create(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    # Manejo de JSON inválido
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return JsonResponse({"error": f"Error al procesar JSON: {str(e)}"}, status=400)

    country_id = payload.get("country")

    # Validar campos obligatorios
    if country_id is None:
        return JsonResponse({"error": "Campos obligatorios faltantes: country"}, status=400)

    try:
        # Preparar datos para crear el historial
        brand_data = {
            'name': payload.get("name"),
            'description': payload.get('description'),
            'country_id': country_id,
        }

        # Filtrar valores None para campos opcionales
        filtered_data = {k: v for k, v in brand_data.items() if v is not None}

        b = Brand.objects.create(**filtered_data)

        # Preparar respuesta con todos los campos del historial creado
        response_data = {
            "message": "Marca creada exitosamente",
            "brand": {
                "id": b.id,
                "name": b.name,
                "description": b.description,
                "country": (
                    {"id": b.country_id, "name": b.country.name}
                    if b.country else None
                ),
                "created_at": to_peru_iso(b.created_at),
                "updated_at": to_peru_iso(b.updated_at)
            }
        }

        return JsonResponse(response_data, status=201)
    except Exception as e:
        return JsonResponse({"error": f"Error al crear la marca: {str(e)}"}, status=500)

@csrf_exempt
@api_view(["PUT", "PATCH"]) 
@authentication_classes([JWTAuthentication, SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def brand_update(request, pk):
    """
    Endpoint PUT para actualizar una marca existente
    """
    if request.method != "PUT":
        return HttpResponseNotAllowed(["PUT"])

    try:
        # Buscar el historial activo
        brand = Brand.objects.get(pk=pk)
    except Brand.DoesNotExist:
        return JsonResponse({"error": "Marca no encontrada o eliminada"}, status=404)

    # Manejo de JSON inválido
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return JsonResponse({"error": f"Error al procesar JSON: {str(e)}"}, status=400)

    # Campos permitidos para actualización
    allowed_fields = {
        'name': 'name',
        'description': 'description',
        'country': 'country_id',
    }

    try:
        with transaction.atomic():
            # Actualizar campos permitidos
            for field_name, model_field in allowed_fields.items():
                if field_name in payload:
                    value = payload[field_name]
                    setattr(brand, model_field, value)
            
            # Guardar los cambios
            brand.save()
            
            # Preparar respuesta con datos actualizados
            updated_data = {
                "id": brand.id,
                "name": brand.name,
                "description": brand.description,
                "country": (
                    {"id": brand.country_id, "name": brand.country.name}
                    if brand.country else None
                ),
                "updated_at": to_peru_iso(brand.updated_at)
            }
            
            return JsonResponse({
                "message": "Marca actualizada exitosamente",
                "brand": updated_data
            }, status=200)
            
    except Exception as e:
        return JsonResponse({"error": f"Error al actualizar la marca: {str(e)}"}, status=500)

@csrf_exempt
@api_view(["DELETE"]) 
@authentication_classes([JWTAuthentication, SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def brand_delete(request, pk):
    if request.method != "DELETE":
        return HttpResponseNotAllowed(["DELETE"])
    
    try:
        b = Brand.objects.get(pk=pk)
    except Brand.DoesNotExist:
        return JsonResponse({"error":"No encontrado"}, status=404)
    
    b.delete()
    return JsonResponse({"status": "deleted"})

@csrf_exempt
@api_view(["GET"]) 
@authentication_classes([JWTAuthentication, SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def brand_detail(request, pk):
    """
    GET - Obtener marca específica
    """
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    
    try:
        brand = Brand.objects.select_related("country").get(pk=pk)
        data = {
            "id": brand.id,
            "name": brand.name,
            "description": brand.description,
            "country": (
                {"id": brand.country_id, "name": brand.country.name}
                if brand.country else None
            ),
            "created_at": to_peru_iso(brand.created_at),
            "updated_at": to_peru_iso(brand.updated_at)
        }
        return JsonResponse(data)
    except Brand.DoesNotExist:
        return JsonResponse({"error": "Marca no encontrada"}, status=404)