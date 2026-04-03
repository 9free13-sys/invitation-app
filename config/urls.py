from django.contrib import admin
from django.urls import path, include
from dashboard.views import home, create_invite
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('create/', create_invite, name='create_invite'),
    path('event/', include('events.urls')),
    path('', include('guests.urls')),
    path('', include('accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)