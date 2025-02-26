from django.urls import path
from . import views

urlpatterns = [
    path('', views.sse_view, name='sse_view'),
    path('send_message/', views.send_message, name='send_message'),
]
