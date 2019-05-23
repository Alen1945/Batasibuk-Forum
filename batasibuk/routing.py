from channels.routing import ProtocolTypeRouter,URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
import chat.routing
import notifier.routing

application=ProtocolTypeRouter({
	'websocket':AllowedHostsOriginValidator(
		AuthMiddlewareStack(
			URLRouter(
					chat.routing.websocket_urlpatterns+\
					notifier.routing.websocket_urlpatterns
				)
			)
		)
	})