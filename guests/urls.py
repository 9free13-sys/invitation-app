from django.urls import path
from . import views

urlpatterns = [
    path('confirm/<int:guest_id>/', views.confirm_guest, name='confirm_guest'),
    path('decline/<int:guest_id>/', views.decline_guest, name='decline_guest'),
    path('invite/<uuid:token>/<str:action>/', views.invite_response, name='invite_response'),
    path('guests/', views.guest_list, name='guest_list'),   
]