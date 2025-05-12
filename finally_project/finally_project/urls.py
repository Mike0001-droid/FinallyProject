from django.contrib import admin
from django.urls import path, include
from account.views import MyTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf import settings
from api import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('api.urls', namespace='')),
    path('', include('account.urls', namespace='')),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/create/', MyTokenObtainPairView.as_view(), name='token_auth'),
    path('calendar/', views.calendar_view, name='calendar'),

]


if settings.DEBUG:
    from rest_framework.documentation import include_docs_urls
    urlpatterns.append(path('api/', include_docs_urls(title='API docs')))
