import json
import os
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from ..models.employee import Employees
from ..serializers.employee import EmployeeSerializer
from datetime import datetime
from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication


def _json_body(request):
    try:
        return json.loads(request.body.decode() or "{}")
    except Exception:
        return {}


class EmployeeViewSet(viewsets.ModelViewSet):

    serializer_class = EmployeeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "name",
        "last_name_paternal",
        "last_name_maternal",
        "document_number",
        "document_type",
        "email",
        "phone",
        "address",
        # búsqueda por nombres de ubicaciones (FK)
        "region__name",
        "province__name",
        "district__name",
    ]

    def get_queryset(self):
        """
        - Usa select_related para evitar N+1 en las FKs de ubicación.
        - Filtra por activo/inactivo (param 'active').
        - Filtra opcionalmente por IDs de region/province/district.
        """
        qs = (
            Employees.objects.select_related("region", "province", "district")
            .all()
        )

        # filtros por ubicación (IDs)
        region = self.request.query_params.get("region")
        province = self.request.query_params.get("province")
        district = self.request.query_params.get("district")
        if region:
            qs = qs.filter(region_id=region)
        if province:
            qs = qs.filter(province_id=province)
        if district:
            qs = qs.filter(district_id=district)

        return qs

@csrf_exempt
@api_view(["GET"]) 
@authentication_classes([JWTAuthentication, SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def employee_list(request):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    
    qs = Employees.objects.select_related("document_type", "rol", "region", "province", "district")
    data = []
    for e in qs:
        data.append({
            "id": e.id,
            "name": e.name,
            "last_name_paternal": e.last_name_paternal,
            "last_name_maternal": e.last_name_maternal,
            "full_name": e.get_full_name(),
            "document_type": (
                {"id": e.document_type.id, "name": e.document_type.name}
                if e.document_type else None
            ),
            "document_number": e.document_number,
            "email": e.email,
            "gender": e.gender,
            "phone": e.phone,
            "birth_date": e.birth_date.isoformat() if e.birth_date else None,
            "region": (
                {"id": e.region.id, "name": e.region.name}
                if e.region else None
            ),
            "province": (
                {"id": e.province.id, "name": e.province.name}
                if e.province else None
            ),
            "district": (
                {"id": e.district.id, "name": e.district.name}
                if e.district else None
            ),
            "rol": (
                {"id": e.rol.id, "name": e.rol.name}
                if e.rol else None
            ),
            "salary": e.salary,
            "address": e.address,
            "photo_url": e.get_photo_url(),
            "created_at": e.created_at.isoformat() if e.created_at else None,
            "updated_at": e.updated_at.isoformat() if e.updated_at else None
        })
    return JsonResponse({"employees": data})


@csrf_exempt
@api_view(["POST"]) 
@authentication_classes([JWTAuthentication, SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def employee_create(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return JsonResponse({"error": f"Error al procesar JSON: {str(e)}"}, status=400)

    try:
        birth_date_str = payload.get("birth_date")

        if not birth_date_str:
            birth_date = None
        else:
            try:
                birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({"error": "Formato de fecha inválido. Usa AAAA-MM-DD."}, status=400)

        employee_data = {
            'name': payload.get('name'),
            'last_name_paternal': payload.get('last_name_paternal'),
            'last_name_maternal': payload.get('last_name_maternal'),
            'document_type_id': payload.get('document_type'),
            'document_number': payload.get('document_number'),
            'email': payload.get('email'),
            'gender': payload.get('gender'),
            'phone': payload.get('phone'),
            'birth_date': birth_date,
            'region_id': payload.get('region'),
            'province_id': payload.get('province'),
            'district_id': payload.get('district'),
            'rol_id': payload.get('rol'),
            'salary': payload.get('salary'),
            'address': payload.get('address'),
        }

        # Usar el serializer para validar y crear
        serializer = EmployeeSerializer(data=employee_data)
        
        if serializer.is_valid():
            employee = serializer.save()
        else:
            # Devolver errores de validación
            return JsonResponse({"errors": serializer.errors}, status=400)

        # Metadata para auditoría (detalle de la acción)
        try:
            request._audit_metadata = {
                "action": "REGISTRAR_EMPLEADO",
                "employee": {
                    "id": employee.id,
                    "email": getattr(employee, "email", None),
                    "document_number": getattr(employee, "document_number", None),
                    "full_name": employee.get_full_name() if hasattr(employee, "get_full_name") else None,
                },
            }
        except Exception:
            pass
        
        # Respuesta usando el serializer para obtener el formato correcto
        response_data = {
            "message": "Empleado creado exitosamente",
            "employee": serializer.data
        }
        
        return JsonResponse(response_data, status=201)
    except Exception as e:
        return JsonResponse({"error": f"Error al crear al empleado: {str(e)}"}, status=500)


@csrf_exempt
@api_view(["PUT", "PATCH"]) 
@authentication_classes([JWTAuthentication, SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def employee_update(request, pk):
    if request.method not in ["PUT", "PATCH"]:
        return HttpResponseNotAllowed(["PUT", "PATCH"])
    
    # Buscar empleado
    try:
        employee = Employees.objects.get(pk=pk)
    except Employees.DoesNotExist:
        return JsonResponse({"error": "Empleado no encontrado"}, status=404)
    
    # Leer JSON
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return JsonResponse({"error": f"Error al procesar JSON: {str(e)}"}, status=400)
    
    # Campos permitidos
    allowed_fields = {
        'name': 'name',
        'last_name_paternal': 'last_name_paternal',
        'last_name_maternal': 'last_name_maternal',
        'document_type': 'document_type_id',
        'document_number': 'document_number',
        'email': 'email',
        'gender': 'gender',
        'phone': 'phone',
        'birth_date': 'birth_date',
        'region': 'region_id',
        'province': 'province_id',
        'district': 'district_id',
        'rol': 'rol_id',
        'salary': 'salary',
        'address': 'address',
    }

    # Preparar datos para el serializer
    update_data = {}
    for field_name, model_field in allowed_fields.items():
        if field_name in payload:
            value = payload[field_name]
            # Si el campo es fecha, convertirla correctamente
            if field_name == "birth_date" and value:
                from datetime import date
                try:
                    value = date.fromisoformat(value)
                except ValueError:
                    return JsonResponse({"error": "Formato de fecha inválido. Usa YYYY-MM-DD."}, status=400)
            update_data[model_field] = value
    
    # Usar el serializer para validar y actualizar
    serializer = EmployeeSerializer(employee, data=update_data, partial=True)
    
    if serializer.is_valid():
        updated_employee = serializer.save()
    else:
        return JsonResponse({"errors": serializer.errors}, status=400)
    
    # Respuesta usando el serializer para obtener el formato correcto
    return JsonResponse({
        "message": "Empleado actualizado exitosamente",
        "employee": serializer.data
    }, status=200)



@csrf_exempt
@api_view(["DELETE"]) 
@authentication_classes([JWTAuthentication, SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def employee_delete(request, pk):
    if request.method != "DELETE":
        return HttpResponseNotAllowed(["DELETE"])
    
    try:
        e = Employees.objects.get(pk=pk)
    except Employees.DoesNotExist:
        return JsonResponse({"error": "No encontrado"}, status=404)
    
    e.delete()
    return JsonResponse({"message": "Empleado eliminado exitosamente",
                         "status": "deleted",
                         "employee_id": pk})


@csrf_exempt
@api_view(["GET"]) 
@authentication_classes([JWTAuthentication, SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def employee_detail(request, pk):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    
    try:
        employee = Employees.objects.select_related("document_type", "rol", "region", "province", "district").get(pk=pk)
        data = {
            "id": employee.id,
            "name": employee.name,
            "last_name_paternal": employee.last_name_paternal,
            "last_name_maternal": employee.last_name_maternal,
            "full_name": employee.get_full_name(),
            "document_type": (
                {"id": employee.document_type.id, "name": employee.document_type.name}
                if employee.document_type else None
            ),
            "document_number": employee.document_number,
            "email": employee.email,
            "gender": employee.gender,
            "phone": employee.phone,
            "birth_date": employee.birth_date.isoformat() if employee.birth_date else None,
            "region": (
                {"id": employee.region.id, "name": employee.region.name}
                if employee.region else None
            ),
            "province": (
                {"id": employee.province.id, "name": employee.province.name}
                if employee.province else None
            ),
            "district": (
                {"id": employee.district.id, "name": employee.district.name}
                if employee.district else None
            ),
            "rol": (
                {"id": employee.rol.id, "name": employee.rol.name}
                if employee.rol else None
            ),
            "salary": employee.salary,
            "address": employee.address,
            "photo_url": employee.get_photo_url(),
            "created_at": employee.created_at.isoformat() if employee.created_at else None,
            "updated_at": employee.updated_at.isoformat() if employee.updated_at else None
        }
        return JsonResponse(data)
    except Employees.DoesNotExist:
        return JsonResponse({"error": "Empleado no encontrado"}, status=404)

@csrf_exempt
@api_view(["POST"]) 
@authentication_classes([JWTAuthentication, SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def employee_photo_upload(request, pk):
    """POST: Subir foto de empleado"""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    
    try:
        employee = Employees.objects.get(pk=pk)
    except Employees.DoesNotExist:
        return JsonResponse({"error": "Empleado no encontrado"}, status=404)
    
    if 'photo' not in request.FILES:
        return JsonResponse({"error": "No se encontró el archivo 'photo' en la petición"}, status=400)
    
    photo_file = request.FILES['photo']
    
    # Validar que sea una imagen
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
    if photo_file.content_type not in allowed_types:
        return JsonResponse({"error": "Tipo de archivo no permitido. Solo se permiten imágenes (JPEG, PNG, GIF)"}, status=400)
    
    # Validar tamaño (máximo 5MB)
    if photo_file.size > 5 * 1024 * 1024:
        return JsonResponse({"error": "El archivo es demasiado grande. Máximo 5MB"}, status=400)
    
    try:
        # Eliminar foto anterior si existe
        if employee.photo:
            if os.path.isfile(employee.photo.path):
                os.remove(employee.photo.path)
        
        # Guardar nueva foto
        employee.photo = photo_file
        employee.save()
        
        return JsonResponse({
            "message": "Foto subida exitosamente",
            "photo_url": employee.get_photo_url()
        }, status=200)
        
    except Exception as e:
        return JsonResponse({"error": f"Error al subir la foto: {str(e)}"}, status=500)


@csrf_exempt
@api_view(["PUT"]) 
@authentication_classes([JWTAuthentication, SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def employee_photo_update(request, pk):
    """PUT: Actualizar foto de empleado - Usa POST internamente"""
    if request.method != "PUT":
        return HttpResponseNotAllowed(["PUT"])
    
    try:
        employee = Employees.objects.get(pk=pk)
    except Employees.DoesNotExist:
        return JsonResponse({"error": "Empleado no encontrado"}, status=404)
    
    # Para PUT, redirigir a la función de upload que ya funciona
    # Cambiar el método a POST temporalmente para que Django parsee los archivos
    request.method = 'POST'
    
    # Llamar a la función de upload que ya funciona
    return employee_photo_upload(request, pk)


@csrf_exempt
@api_view(["DELETE"]) 
@authentication_classes([JWTAuthentication, SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def employee_photo_delete(request, pk):
    """DELETE: Eliminar foto de empleado"""
    if request.method != "DELETE":
        return HttpResponseNotAllowed(["DELETE"])
    
    try:
        employee = Employees.objects.get(pk=pk)
    except Employees.DoesNotExist:
        return JsonResponse({"error": "Empleado no encontrado"}, status=404)
    
    if not employee.photo:
        return JsonResponse({"error": "El empleado no tiene foto para eliminar"}, status=400)
    
    try:
        # Eliminar archivo físico si existe
        if os.path.isfile(employee.photo.path):
            os.remove(employee.photo.path)
        
        # Limpiar campo en la base de datos
        employee.photo = None
        employee.save()
        
        return JsonResponse({
            "message": "Foto eliminada exitosamente"
        }, status=200)
        
    except Exception as e:
        return JsonResponse({"error": f"Error al eliminar la foto: {str(e)}"}, status=500)
