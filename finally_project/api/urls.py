from rest_framework import routers
from api import views

router = routers.DefaultRouter()

router.register(r'taski', views.TaskViewSet, basename='taski')
router.register(r'evaluations', views.EvaluationViewSet, basename='evaluations')
router.register(r'meetings', views.MeetingViewSet, basename='meetings')
router.register(r'by_period', views.ByPeriodViewSet, basename='by-period')
router.register(r'group_manager', views.GroupManagerViewSet, basename='group-manager')



app_name = 'api'
urlpatterns = router.urls



