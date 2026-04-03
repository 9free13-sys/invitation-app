from django.urls import path
from . import views


urlpatterns = [
    path('', views.guest_list, name='guest_list'),
    path('confirm/<uuid:token>/', views.confirm_guest, name='confirm_guest'),
    path('decline/<uuid:token>/', views.decline_guest, name='decline_guest'),
    path('invite/<uuid:token>/<str:action>/', views.invite_response, name='invite_response'),

    # eliminar convidado
    path('delete/<int:guest_id>/', views.delete_guest, name='delete_guest'),
]