from rest_framework import routers
from api import views

router = routers.DefaultRouter()

router.register(r'tasks', views.TaskViewSet, basename='tasks')
router.register(r'evaluations', views.EvaluationViewSet, basename='evaluations')


app_name = 'api'
urlpatterns = router.urls



