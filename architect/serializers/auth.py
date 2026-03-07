from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from users_profiles.models.user_verification_code import UserVerificationCode

User = get_user_model()
try:
    from audits.services import AuditService
except Exception:
    AuditService = None

try:
    from users_profiles.services.verification_service import VerificationService
except Exception:
    VerificationService = None


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255, required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True)
    code = serializers.CharField(required=False, allow_null=True, allow_blank=True, write_only=True)
    challenge_id = serializers.IntegerField(required=False, write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        code = data.get('code')
        challenge_id = data.get('challenge_id')

        if not email or not password:
            raise serializers.ValidationError(_('Se requieres email y contraseña.'))

        # Buscar usuario por email y verificar contraseña
        try:
            user = User.objects.get(email=email)
            if not user.check_password(password):
                user = None
        except User.DoesNotExist:
            user = None

        if user is None:
            raise AuthenticationFailed(_('Credenciales inválidas.'))
        
        if not user.is_active:
            raise AuthenticationFailed(_('Cuenta no activada.'))

        # Paso 1: no se envió código → generar y enviar código 2FA
        if not code:
            if not VerificationService:
                raise AuthenticationFailed(_('El servicio de verificación no está disponible.'))

            try:
                verification_code = VerificationService.send_verification_email(
                    user=user,
                    verification_type='login_2fa',
                )
            except Exception:
                # Si falla el envío del correo, no permitir continuar
                raise AuthenticationFailed(_('No se pudo enviar el código de verificación. Intenta nuevamente.'))

            return {
                '2fa_required': True,
                'challenge_id': verification_code.id,
                'email': user.email,
                'message': _('Se ha enviado un código de verificación a tu correo electrónico.'),
            }

        # Paso 2: se envió código → validar código 2FA y emitir tokens
        qs = UserVerificationCode.objects.filter(
            user=user,
            verification_type='login_2fa',
            is_used=False,
        )
        # Si viene challenge_id, lo usamos como filtro adicional (opcional)
        if challenge_id:
            qs = qs.filter(id=challenge_id)

        verification = qs.order_by('-created_at').first()
        if not verification:
            raise AuthenticationFailed(_('El código de verificación no es válido o ya fue utilizado.'))

        # Verificar estado del código
        if verification.is_locked():
            raise AuthenticationFailed(_('El código está temporalmente bloqueado por múltiples intentos fallidos.'))

        if verification.is_expired():
            verification.mark_as_used()
            raise AuthenticationFailed(_('El código de verificación ha expirado.'))

        if verification.code != str(code).strip():
            # Intento fallido
            verification.increment_failed_attempts()
            if verification.failed_attempts >= 5:
                verification.lock_temporarily(minutes=15)
            raise AuthenticationFailed(_('El código de verificación es incorrecto.'))

        # Código correcto → marcar como usado
        verification.mark_as_used()

        # Emitir tokens JWT
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        # Registrar sesión de auditoría (si la app está instalada)
        request = self.context.get("request")
        if AuditService and request is not None:
            try:
                session = AuditService.open_login_session(
                    request=request,
                    user=user,
                    refresh=refresh,
                    access=access,
                )
                session_id = session.id
            except Exception:
                session_id = None
        else:
            session_id = None

        return {
            'email': user.email,
            'refresh': str(refresh),
            'access': str(access),
            'user_id': user.id,
            'audit_session_id': session_id,
            '2fa_verified': True,
        }


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, required=True)
    user_name = serializers.CharField(required=True, max_length=150)
    document_number = serializers.CharField(required=True, max_length=255)

    class Meta:
        model = User
        fields = ('user_name', 'email', 'document_number', 'password', 'password_confirm')

    def validate_password(self, value):
        # Validación personalizada de contraseña
        if len(value) < 8:
            raise serializers.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        
        # Verificar que no sea una contraseña común
        common_passwords = ['password', '123456', '12345678', 'qwerty', 'abc123', 'password123', 'admin', 'letmein']
        if value.lower() in common_passwords:
            raise serializers.ValidationError("Esta contraseña es demasiado común. Elige una contraseña más segura.")
        
        return value

    def validate_document_number(self, value):
        if not value:
            raise serializers.ValidationError("El número de documento es obligatorio.")
        
        # Verificar que sea único
        if User.objects.filter(document_number=value).exists():
            raise serializers.ValidationError("Este número de documento ya está registrado.")
        
        return value

    def validate_user_name(self, value):
        if not value:
            raise serializers.ValidationError("El nombre de usuario es obligatorio.")
        
        # Verificar que sea único
        if User.objects.filter(user_name=value).exists():
            raise serializers.ValidationError("Este nombre de usuario ya está registrado.")
        
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Las contraseñas no coinciden"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        user.is_active = True  # Asegurar que el usuario esté activo
        user.save()
        return user 