from rest_framework.routers import DefaultRouter
from .views import AssistantViewSet, FileViewSet, ThreadViewSet

router = DefaultRouter()
router.register(r'assistants', AssistantViewSet)
router.register(r'files', FileViewSet)
router.register(r'threads', ThreadViewSet)

urlpatterns = router.urls