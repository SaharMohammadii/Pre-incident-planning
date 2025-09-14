from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TemplateViewSet, FormResponseViewSet

router = DefaultRouter()
router.register(r"templates", TemplateViewSet, basename="template")
router.register(r"responses", FormResponseViewSet, basename="response")

urlpatterns = [
    path("api/", include(router.urls)),
]
