from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('create/', views.create_event, name='create_event'),
    path('<int:event_id>/', views.event_detail, name='event_detail'),
    path('<int:event_id>/guests/', views.event_guests, name='event_guests'),
    path('<int:event_id>/export/excel/', views.export_guests_excel, name='export_guests_excel'),
    path('<int:event_id>/export/pdf/', views.export_guests_pdf, name='export_guests_pdf'),
    path('<int:event_id>/send/emails/', views.send_invites_email, name='send_invites_email'),
    path('delete/<int:event_id>/', views.delete_event, name='delete_event'),
]