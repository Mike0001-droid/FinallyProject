from rest_framework import routers
from account import views

router = routers.DefaultRouter()

router.register(r'', views.MyUserViewSet, basename='users')
router.register(r'teams', views.TeamViewSet, basename='teams')

app_name = 'account'
urlpatterns = router.urls



