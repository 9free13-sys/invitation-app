from django.urls import path
from . import views

urlpatterns = [
    path('guests/', views.guest_list, name='guest_list'),

    path('confirm/<uuid:token>/', views.confirm_guest, name='confirm_guest'),
    path('decline/<uuid:token>/', views.decline_guest, name='decline_guest'),

    # 🔴 NOVO LINK CURTO
    path('invite/<slug:slug>/', views.invite_page, name='invite_page'),
    path('invite/<slug:slug>/<str:action>/', views.invite_response, name='invite_response'),

    path('delete/<int:guest_id>/', views.delete_guest, name='delete_guest'),
]