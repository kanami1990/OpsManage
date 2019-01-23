from channels.routing import route
from OpsManage.djchannels import notices,chats
from logmonitor.consumer import ws_connect,ws_disconnect

# The channel routing defines what channels get handled by what consumers,
# including optional matching on message attributes. In this example, we route
# all WebSocket connections to the class-based BindingConsumer (the consumer
# class itself specifies what channels it wants to consume)
channel_routing = [
#     wssh.webterminal.as_route(path = r'^/ws/webssh/(?P<id>[0-9]+)/$'),
    notices.WebNotice.as_route(path = r'^/ws/notice/(?P<username>.+)/$'),
    route('websocket.connect', ws_connect),
    route('websocket.disconnect', ws_disconnect),
    # notices.WebNotice.as_route(path = r'^/ws/log/(?P<id>.+)/$'),
#     chats.WebChat.as_route(path = r'^/ws/chats/$'),
]