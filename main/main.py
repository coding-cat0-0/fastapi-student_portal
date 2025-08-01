from fastapi import FastAPI
from fastapi import FastAPI, Depends, HTTPException, status 
from models import model
from database.structure import get_db, engine, Base
from sqlalchemy.orm import Session
from routers import actions_teach, actions_stu, login
from admin import admin_tasks
from websockets_router import login_websocket
from fastapi_socketio import SocketManager
from websockets_router import core_socketio
from websockets_router.core_socketio import socket_manager

app = FastAPI()
socket_manager = SocketManager(app=app)
core_socketio.socket_manager = socket_manager
core_socketio.handle_socket_manager()
# Base.metadata.create_all(engine)

app.include_router(actions_teach.router)
app.include_router(actions_stu.router)
app.include_router(admin_tasks.router)
app.include_router(login.router)
app.include_router(login_websocket.router)


