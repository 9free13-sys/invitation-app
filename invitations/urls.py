from django.urls import path
from . import views

urlpatterns = [
    path('my-invitations/', views.my_invitations, name='my_invitations'),
]