from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/',     include('Apps.Users.urls')),
    path('api/cameras/',   include('Apps.Cameras.urls')),
    path('api/detection/', include('Apps.detection.urls')),
    path('api/alerts/',    include('Apps.alertes.urls')),
    path('api/audits/',    include('Apps.audits.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)