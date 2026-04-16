from django.urls import path
from . import views

urlpatterns = [
    path('guests/', views.guest_list, name='guest_list'),

    path('confirm/<uuid:token>/', views.confirm_guest, name='confirm_guest'),
    path('decline/<uuid:token>/', views.decline_guest, name='decline_guest'),

    path('invite/<uuid:token>/', views.invite_page_by_token, name='invite_page_by_token'),
    path('invite/<uuid:token>/<str:action>/', views.invite_response_by_token, name='invite_response_by_token'),

    path('invite/<slug:slug>/', views.invite_page, name='invite_page'),
    path('invite/<slug:slug>/<str:action>/', views.invite_response, name='invite_response'),

    path('invite-status/<slug:slug>/', views.invite_status, name='invite_status'),

    path('event/<int:event_id>/scan-qr/', views.scan_qr_page, name='scan_qr_page'),
    path('event/<int:event_id>/scan-qr/validate/', views.validate_qr_code, name='validate_qr_code'),

    path('delete/<int:guest_id>/', views.delete_guest, name='delete_guest'),
]