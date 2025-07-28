from fastapi import FastAPI
from fastapi import FastAPI, Depends, HTTPException, status 
from models import model
from database.structure import get_db, engine, Base
from sqlalchemy.orm import Session
from routers import actions_teach, actions_stu, login
from admin import admin_tasks

app = FastAPI()

# Base.metadata.create_all(engine)

app.include_router(actions_teach.router)
app.include_router(actions_stu.router)
app.include_router(admin_tasks.router)
app.include_router(login.router)


