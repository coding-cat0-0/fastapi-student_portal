from websockets_router.login_websocket import active_connections
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from models import model
import redis
import json
import threading
import asyncio
from database.structure import get_db



def listen_notifications():
  r = redis.Redis(host = 'localhost', port = 6379, db = 0) #redis.Redis(): Creates a Redis client to talk to your Redis server.
  pubsub = r.pubsub() # .pubsub(): Creates a Pub/Sub object (to listen to Redis channels).
  pubsub.subscribe('notifications') # .subscribe('notifications'): Subscribes to the channel where your login 
  #notifications are being published.
  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)

  
  for message in pubsub.listen():
          
        if message['type'] == 'message' :
          #try:
            data = json.loads(message['data'])
            decode = message['data'].decode('utf-8')
            email = data['email']
            text = data['message']
            ws = active_connections.get(email)
            if ws:
                print(f"{email}: {text}")    
                def mark_delivered():
                        db:Session = next(get_db())
                        notification = db.query(model.Notifications).filter(model.Notifications.email == email,
                            model.Notifications.message == text, model.Notifications.delivered==False).all()
                        for msgs in notification:
                                    msgs.delivered = True
                        db.commit() 
                mark_delivered()        
                asyncio.run_coroutine_threadsafe(ws.send_text(text), loop) 
            else:
                    print(f"no active connection for {email}")
 
