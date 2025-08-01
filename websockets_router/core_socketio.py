from fastapi_socketio import SocketManager
from fastapi_socketio import SocketManager
from websockets_router.login_websocket import active_connections

socket_manager = None

def handle_socket_manager():
    if socket_manager is None:
        raise Exception("Socket manager hasn't been initialised")

    @socket_manager.on('notify')
    async def handle_notify(sid, data):
      email = data['email']
      message = data['message']
      ws = active_connections.get(email)
      if ws:
        await ws.send_text(message)
