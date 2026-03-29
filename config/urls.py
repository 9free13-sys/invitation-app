from django.contrib import admin
from django.urls import path, include
from dashboard.views import create_invite


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('events/', include('events.urls')),
    path('', include('guests.urls')),
    path('create/', create_invite, name='create_invite'),
]