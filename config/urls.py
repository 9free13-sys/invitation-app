from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # dashboard como homepage
    path('', include('dashboard.urls')),

    # apps com prefixo claro
    path('event/', include('events.urls')),
    path('notifications/', include('notifications.urls')),

    # convidados (mantém na raiz se for necessário para links públicos)
    path('invite/', include('guests.urls')),

    # contas (login, register, etc.)
    path('', include('accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)