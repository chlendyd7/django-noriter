# uvicorn sse.asgi:application --host 0.0.0.0 --port 8000

import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import sockt.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sse.settings")
django.setup()

# application = get_asgi_application()
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # "websocket": AuthMiddlewareStack(
    #     URLRouter(
    #         sockt.routing.websocket_urlpatterns,
    #         asyc.urls.sse_urlpatterns
    #     )
    # ),
})
