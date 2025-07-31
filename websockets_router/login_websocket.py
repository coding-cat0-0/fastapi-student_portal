from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from database.structure import get_db
from authentication.oauth2_ws import get_current_ws

router = APIRouter()
active_connections : dict[str, WebSocket]={}

@router.websocket('/ws/login/notification')
async def websocket_endpoint(websocket : WebSocket, db:Session = Depends(get_db)):
    current_ws = await get_current_ws(websocket, db)
    if not current_ws:
        print("User validation failed. Closing socket.")
        return
    await websocket.accept() # opens the connection
    print("connection open")

    email =   current_ws.email 

#    (
#    current_ws.email 
#    if hasattr(current_ws, "email") 
#    else current_ws.admin_email)
    
    active_connections[email] = websocket
    print("WebSocket stored email:", email)
    print(active_connections)
    try: 
        while True:
            data = await websocket.receive_text() # keeps it alive not significant what you put here
            print(f"{email} sent : {data}") # same as above
    except WebSocketDisconnect: 
        active_connections.pop(email, None)
        
     
        