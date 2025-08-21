from rest_framework.routers import DefaultRouter
from .views import AssistantViewSet, FileViewSet, ThreadViewSet, VectorStoreViewSet
from .api_views import (
	AddAssistantView, DeleteAssistantView, UploadFileView, DeleteFileView,
	AddVectorStoreView, DeleteVectorStoreView, CreateThreadView, SendPromptView
)
from django.urls import path

router = DefaultRouter()
router.register(r'assistants', AssistantViewSet)
router.register(r'files', FileViewSet)
router.register(r'threads', ThreadViewSet)

urlpatterns = router.urls
urlpatterns += [
	# Service endpoints
	path('services/add-assistant/', AddAssistantView.as_view(), name='add-assistant'),
	path('services/delete-assistant/<int:pk>/', DeleteAssistantView.as_view(), name='delete-assistant'),
	path('services/upload-file/', UploadFileView.as_view(), name='upload-file'),
	path('services/delete-file/<int:pk>/', DeleteFileView.as_view(), name='delete-file'),
	path('services/add-vectorstore/', AddVectorStoreView.as_view(), name='add-vectorstore'),
	path('services/delete-vectorstore/<int:pk>/', DeleteVectorStoreView.as_view(), name='delete-vectorstore'),
	path('services/create-thread/', CreateThreadView.as_view(), name='create-thread'),
	path('services/send-prompt/', SendPromptView.as_view(), name='send-prompt'),
]