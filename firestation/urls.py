from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenVerifyView, TokenRefreshView



authentication_routes = [
    path("accounts/", include('account.urls')),
    path('auth/', include('djoser.urls')),
    path('auth/jwt/refresh/', TokenRefreshView.as_view(), name='jwt-refresh'),
    path('auth/jwt/verify/', TokenVerifyView.as_view(), name='jwt-verify'),
]


local_apps_routes = [
    path('management/', include('management.urls')),
    path('building/', include('building.urls')),
    path('form/', include('FormCreator.urls')),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    
]

urlpatterns += authentication_routes + local_apps_routes


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)