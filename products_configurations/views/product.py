import json
import os
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from ..models.product import Product
from ..serializers.product import ProductSerializer
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


class ProductViewSet(viewsets.ModelViewSet):

    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "name",
        "model",
        "category",
        "supplier",
        "brand",
        # búsqueda por nombres de ubicaciones (FK)
        "brand__name",
        "category__name",
        "supplier__name",
    ]

@csrf_exempt
@api_view(["GET"]) 
@authentication_classes([JWTAuthentication, SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def product_list(request):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    
    qs = Product.objects.select_related("category", "supplier", "brand")
    data = []
    for p in qs:
        data.append({
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "model": p.model,
            "unit_price": p.unit_price,
            "sales_price": p.sales_price,
            "stock": p.stock,
            "discount": p.discount,
            "photo_url": p.get_photo_url(),
            "category": (
                {"id": p.category.id, "name": p.category.name}
                if p.category else None
            ),
            "supplier": (
                {"id": p.supplier.id, "name": p.supplier.company_name}
                if p.supplier else None
            ),
            "brand": (
                {"id": p.brand.id, "name": p.brand.name}
                if p.brand else None
            ),
            "state": p.state,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None
        })
    return JsonResponse({"products": data})


@csrf_exempt
@api_view(["POST"]) 
@authentication_classes([JWTAuthentication, SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def product_create(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return JsonResponse({"error": f"Error al procesar JSON: {str(e)}"}, status=400)

    try:
        product_data = {
            'name': payload.get('name'),
            'description': payload.get('description'),
            'model': payload.get('model'),
            'unit_price': payload.get('unit_price'),
            'sales_price': payload.get('sales_price'),
            'stock': payload.get('stock'),
            'discount': payload.get('discount'),
            'category_id': payload.get('category_id'),
            'supplier_id': payload.get('supplier_id'),
            'brand_id': payload.get('brand_id'),
            'state': payload.get('state'),
        }

        # Usar el serializer para validar y crear
        serializer = ProductSerializer(data=product_data)
        
        if serializer.is_valid():
            product = serializer.save()
        else:
            # Devolver errores de validación
            return JsonResponse({"errors": serializer.errors}, status=400)
        
        # Respuesta usando el serializer para obtener el formato correcto
        response_data = {
            "message": "Producto creado exitosamente",
            "product": serializer.data
        }
        
        return JsonResponse(response_data, status=201)

    except Exception as e:
        return JsonResponse({"error": f"Error al crear el producto: {str(e)}"}, status=500)

@csrf_exempt
@api_view(["PUT", "PATCH"]) 
@authentication_classes([JWTAuthentication, SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def product_update(request, pk):
    if request.method not in ["PUT", "PATCH"]:
        return HttpResponseNotAllowed(["PUT", "PATCH"])
    
    # Buscar empleado
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return JsonResponse({"error": "Producto no encontrado"}, status=404)
    
    # Leer JSON
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return JsonResponse({"error": f"Error al procesar JSON: {str(e)}"}, status=400)
    
    # Campos permitidos
    allowed_fields = {
        'name': 'name',
        'description': 'description',
        'model': 'model',
        'unit_price': 'unit_price',
        'sales_price': 'sales_price',
        'stock': 'stock',
        'discount': 'discount',
        'category': 'category_id',
        'supplier': 'supplier_id',
        'brand': 'brand_id',
        'state': 'state',
    }

    # Preparar datos para el serializer
    update_data = {}
    for field_name, model_field in allowed_fields.items():
        if field_name in payload:
            value = payload[field_name]
            update_data[model_field] = value
    
    # Usar el serializer para validar y actualizar
    serializer = ProductSerializer(product, data=update_data, partial=True)
    
    if serializer.is_valid():
        updated_product = serializer.save()
    else:
        return JsonResponse({"errors": serializer.errors}, status=400)
    
    # Respuesta usando el serializer para obtener el formato correcto
    return JsonResponse({
        "message": "Producto actualizado exitosamente",
        "product": serializer.data
    }, status=200)

@csrf_exempt
@api_view(["DELETE"]) 
@authentication_classes([JWTAuthentication, SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def product_delete(request, pk):
    if request.method != "DELETE":
        return HttpResponseNotAllowed(["DELETE"])
    
    try:
        p = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return JsonResponse({"error": "No encontrado"}, status=404)
    
    p.delete()
    return JsonResponse({"message": "Producto eliminado exitosamente",
                         "status": "deleted",
                         "product_id": pk})

@csrf_exempt
@api_view(["GET"]) 
@authentication_classes([JWTAuthentication, SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def product_detail(request, pk):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    
    try:
        product = Product.objects.select_related("category", "supplier", "brand").get(pk=pk)
        data = {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "model": product.model,
            "unit_price": product.unit_price,
            "sales_price": product.sales_price,
            "stock": product.stock,
            "discount": product.discount,
            "photo_url": product.get_photo_url(),
            "category": (
                {"id": product.category.id, "name": product.category.name}
                if product.category else None
            ),
            "supplier": (
                {"id": product.supplier.id, "name": product.supplier.company_name}
                if product.supplier else None
            ),
            "brand": (
                {"id": product.brand.id, "name": product.brand.name}
                if product.brand else None
            ),
            "state": product.state,
            "created_at": product.created_at.isoformat() if product.created_at else None,
            "updated_at": product.updated_at.isoformat() if product.updated_at else None
        }
        return JsonResponse(data)
    except Product.DoesNotExist:
        return JsonResponse({"error": "Producto no encontrado"}, status=404)

@csrf_exempt
@api_view(["POST"]) 
@authentication_classes([JWTAuthentication, SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def product_photo_upload(request, pk):
    """POST: Subir foto de producto"""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return JsonResponse({"error": "Producto no encontrado"}, status=404)
    
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
        if product.photo:
            if os.path.isfile(product.photo.path):
                os.remove(product.photo.path)
        
        # Guardar nueva foto
        product.photo = photo_file
        product.save()
        
        return JsonResponse({
            "message": "Foto subida exitosamente",
            "photo_url": product.get_photo_url()
        }, status=200)
        
    except Exception as e:
        return JsonResponse({"error": f"Error al subir la foto: {str(e)}"}, status=500)


@csrf_exempt
@api_view(["PUT"]) 
@authentication_classes([JWTAuthentication, SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def product_photo_update(request, pk):
    """PUT: Actualizar foto de producto"""
    if request.method != "PUT":
        return HttpResponseNotAllowed(["PUT"])
    
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return JsonResponse({"error": "Producto no encontrado"}, status=404)
    
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
        if product.photo:
            if os.path.isfile(product.photo.path):
                os.remove(product.photo.path)
        
        # Guardar nueva foto
        product.photo = photo_file
        product.save()
        
        return JsonResponse({
            "message": "Foto actualizada exitosamente",
            "photo_url": product.get_photo_url()
        }, status=200)
        
    except Exception as e:
        return JsonResponse({"error": f"Error al actualizar la foto: {str(e)}"}, status=500)


@csrf_exempt
@api_view(["DELETE"]) 
@authentication_classes([JWTAuthentication, SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def product_photo_delete(request, pk):
    """DELETE: Eliminar foto de producto"""
    if request.method != "DELETE":
        return HttpResponseNotAllowed(["DELETE"])
    
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return JsonResponse({"error": "Producto no encontrado"}, status=404)
    
    if not product.photo:
        return JsonResponse({"error": "El producto no tiene foto para eliminar"}, status=400)
    
    try:
        # Eliminar archivo físico si existe
        if os.path.isfile(product.photo.path):
            os.remove(product.photo.path)
        
        # Limpiar campo en la base de datos
        product.photo = None
        product.save()
        
        return JsonResponse({
            "message": "Foto eliminada exitosamente"
        }, status=200)
        
    except Exception as e:
        return JsonResponse({"error": f"Error al eliminar la foto: {str(e)}"}, status=500)
