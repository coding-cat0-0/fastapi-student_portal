from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from models import model
from database.structure import get_db
from authentication.oauth2_ws import get_current_ws
from fastapi_socketio import SocketManager

router = APIRouter()


active_connections : dict[str, WebSocket]={}

@router.websocket('/ws/login/notification')
async def websocket_endpoint(websocket : WebSocket, db:Session = Depends(get_db)):
   
    await websocket.accept()
    try: 
       current_ws = await get_current_ws(websocket, db)
       if not current_ws:
         print("User validation failed. Returning from socket handler.")
         return
     
       print("connection open")

       email =   current_ws.email 

       active_connections[email] =  websocket
       print("WebSocket stored email:", email)
       print(active_connections)
       
       notification = db.query(model.Notifications).filter(model.Notifications.email == email,
       model.Notifications.delivered==False).all()
       for msgs in notification:
                     await websocket.send_text(msgs.message) 
                     msgs.delivered = True
       db.commit() 
 
       while True:
            data = await websocket.receive_text() # keeps it alive not significant what you put here
            print(f"{email} sent : {data}") # same as above
    except WebSocketDisconnect: 
        active_connections.pop(email, None)
        
     
        