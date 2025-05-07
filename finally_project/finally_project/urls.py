from django.contrib import admin
from django.urls import path, include
from account.views import MyTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/user/', include('account.urls', namespace='user')),
    path('api/users/token/create/', MyTokenObtainPairView.as_view(), name='token_auth'),
    path('api/users/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
