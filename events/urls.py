from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('create/', views.create_event, name='create_event'),
    path('<int:event_id>/', views.event_detail, name='event_detail'),
    path('<int:event_id>/guests/', views.event_guests, name='event_guests'),
    path('delete/<int:event_id>/', views.delete_event, name='delete_event'),
]