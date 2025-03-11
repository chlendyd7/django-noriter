from django.urls import path
from . import views

urlpatterns = [
    path('connect/', views.sse_connect, name='sse_connect'),
    path('send_message/', views.send_message, name='send_message'),
]
