from django.contrib import admin
from django.urls import path, include
from account.views import MyTokenObtainPairView, LogoutView
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf import settings
from api import views
from django.views.generic import TemplateView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('api.urls', namespace='')),
    path('', include('account.urls', namespace='')),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/create/', MyTokenObtainPairView.as_view(), name='token_auth'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('create/', views.create_meeting, name='create_meeting'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('signup/', TemplateView.as_view(template_name='signup.html'), name='signup'),
    path('logout/', TemplateView.as_view(template_name='logout.html'), name='logout'),
    path('api/logout/', LogoutView.as_view(), name='api_logout'),
    

    
]


if settings.DEBUG:
    from rest_framework.documentation import include_docs_urls
    urlpatterns.append(path('api/', include_docs_urls(title='API docs')))
