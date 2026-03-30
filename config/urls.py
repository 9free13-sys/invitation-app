from django.contrib import admin
from django.urls import path, include
from dashboard.views import home, create_invite

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('create/', create_invite, name='create_invite'),
    path('', include('events.urls')),
    path('', include('guests.urls')),
    path('', include('accounts.urls')),
]