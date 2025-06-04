from rest_framework_simplejwt.authentication import JWTAuthentication


class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_auth = JWTAuthentication()

    def __call__(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated:
            return self.get_response(request)

        try:
            header = self.jwt_auth.get_header(request)
            if header is not None:
                raw_token = self.jwt_auth.get_raw_token(header)
                validated_token = self.jwt_auth.get_validated_token(raw_token)
                user = self.jwt_auth.get_user(validated_token)
                request.user = user
                from django.contrib.auth import login
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                
        except Exception:
            pass
        return self.get_response(request)
