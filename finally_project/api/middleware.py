from django.contrib.auth import login
from django.shortcuts import redirect
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_authenticator = JWTAuthentication()
        self.User = get_user_model()

    def __call__(self, request):
        if self._should_skip_request(request):
            return self.get_response(request)

        try:
            jwt_token = self._get_jwt_token(request)
            
            if jwt_token:
                user = self._authenticate_with_token(jwt_token)
                
                if user and user.is_active:
                    # Логиним пользователя в Django сессии
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    
                    # Если запрос к защищенной странице без авторизации
                    if self._is_protected_path(request.path) and not request.user.is_authenticated:
                        return redirect(f'/login/?next={request.path}')
                    
        except Exception as e:
            logger.error(f"JWT authentication error: {str(e)}", exc_info=True)
            
            # Если ошибка аутентификации и запрос к защищенной странице
            if self._is_protected_path(request.path):
                return redirect(f'/login/?next={request.path}')

        return self.get_response(request)

    def _should_skip_request(self, request):
        skip_paths = [
            '/admin/login/',
            '/login/',
            '/static/',
            '/favicon.ico',
            '/api/auth/login/',
            '/api/auth/refresh/',
        ]
        return any(request.path.startswith(path) for path in skip_paths)

    def _is_protected_path(self, path):
        protected_paths = [
            '/admin/',
            '/calendar/',
            '/tasks/',
        ]
        return any(path.startswith(p) for p in protected_paths)

    def _get_jwt_token(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            return auth_header.split(' ')[1]

        if 'access_token' in request.COOKIES:
            return request.COOKIES['access_token']

        return None

    def _authenticate_with_token(self, raw_token):
        try:
            validated_token = self.jwt_authenticator.get_validated_token(raw_token)
            user_id = validated_token.get('user_id')
            
            if user_id:
                user = self.User.objects.filter(id=user_id).first()
                if user and user.is_active:
                    return user

        except (InvalidToken, AuthenticationFailed) as e:
            logger.warning(f"Invalid JWT token: {str(e)}")
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}", exc_info=True)

        return None