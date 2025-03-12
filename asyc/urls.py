from django.urls import path
from . import views

urlpatterns = [
    path('connect/', views.SSEConsumer.as_asgi(), name='sse_connect'),
    # path('send_message/', views.send_message, name='send_message'),
]
