#!/usr/bin/env python3
"""
Archivo de prueba para verificar que todas las importaciones de 01_architect funcionen correctamente
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Probar importaciones de 01_architect
try:
    print("=== PROBANDO IMPORTACIONES DE 01_ARCHITECT ===")
    
    # Importar modelos
    print("\n Probando modelos...")
    import importlib
    models_module = importlib.import_module('01_architect.models')
    User = models_module.User
    UserVerificationCode = models_module.UserVerificationCode
    Permission = models_module.Permission
    Role = models_module.Role
    print(" User, UserVerificationCode, Permission, Role importados correctamente")
    
    # Importar serializers
    print("\n Probando serializers...")
    serializers_module = importlib.import_module('01_architect.serializers')
    LoginSerializer = serializers_module.LoginSerializer
    RegisterSerializer = serializers_module.RegisterSerializer
    UserSerializer = serializers_module.UserSerializer
    print(" LoginSerializer, RegisterSerializer, UserSerializer importados correctamente")
    
    # Importar vistas
    print("\n Probando vistas...")
    views_module = importlib.import_module('01_architect.views')
    LoginView = views_module.LoginView
    RegisterView = views_module.RegisterView
    UserView = views_module.UserView
    print(" LoginView, RegisterView, UserView importados correctamente")
    
    # Importar servicios
    print("\n️ Probando servicios...")
    services_module = importlib.import_module('01_architect.services')
    AuthService = services_module.AuthService
    UserService = services_module.UserService
    PermissionService = services_module.PermissionService
    print(" AuthService, UserService, PermissionService importados correctamente")
    
    # Importar middleware
    print("\n Probando middleware...")
    middleware_module = importlib.import_module('01_architect.middleware')
    OptionalAuthenticate = middleware_module.OptionalAuthenticate
    print(" OptionalAuthenticate importado correctamente")
    
    # Importar permisos
    print("\n Probando permisos...")
    permissions_module = importlib.import_module('01_architect.permissions')
    IsAdminUser = permissions_module.IsAdminUser
    IsOwnerOrReadOnly = permissions_module.IsOwnerOrReadOnly
    print(" IsAdminUser, IsOwnerOrReadOnly importados correctamente")
    
    # Importar utilidades
    print("\n️ Probando utilidades...")
    utils_module = importlib.import_module('01_architect.utils')
    JWTUtils = utils_module.JWTUtils
    SystemConstants = utils_module.SystemConstants
    print(" JWTUtils, SystemConstants importados correctamente")
    
    # Importar configuración de email
    print("\n Probando configuración de email...")
    email_config_module = importlib.import_module('01_architect.utils.email_config')
    EMAIL_CONFIG = email_config_module.EMAIL_CONFIG
    print(" EMAIL_CONFIG importado correctamente")
    
    print("\n ¡TODAS LAS IMPORTACIONES DE 01_ARCHITECT FUNCIONAN CORRECTAMENTE!")
    print(" La migración fue exitosa")
    
except ImportError as e:
    print(f" Error de importación: {e}")
    print(" Verifica que la estructura 01_architect esté correcta")
    sys.exit(1)
except Exception as e:
    print(f" Error inesperado: {e}")
    print(" Revisa la configuración de Django")
    sys.exit(1) 