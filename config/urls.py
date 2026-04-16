from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('event/', include('events.urls')),
    path('', include('guests.urls')),
    path('', include('accounts.urls')),
    path('', include('invitations.urls')),
    path('notifications/', include('notifications.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)