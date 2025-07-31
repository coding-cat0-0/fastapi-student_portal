from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from schema import user_schema
from models import model
from authentication.oauth2 import create_access_token, get_current_user
from database.structure import get_db, engine
from hasher.hashing import Hash, pwd_context
from typing import List
from email.mime.text import MIMEText
import smtplib
import random
from datetime import datetime, timedelta

from websockets_router.login_websocket import active_connections
import asyncio



router = APIRouter(
    tags=["Authentication"]
)

@router.post('/user/login')
async def login( user: user_schema.LoginUser,
    db: Session = Depends(get_db)):  
    db_user = None
    role = None
    login_user = db.query(model.Users).filter(model.Users.email == user.email).first()
    if login_user and Hash.verify_password(user.password, login_user.password):
        db_user = login_user 
        role = login_user.role
    
    if login_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )       
    
    access_token = create_access_token(data={"role":role,"sub": str(db_user.id)})
    target_email = user.email
    connection = active_connections.get(target_email)
    if connection:
            print("Active WebSocket connections:", active_connections)
            print("Target email:", target_email)
            await connection.send_text(f"{role.capitalize()} with email {target_email} logged in successfully!")  
    else:
        print(f"No websocket with email {target_email} logged in..")
        
    return {"access_token": access_token, "token_type": "bearer", "role": role}


def send_otp(to_email: str, otp: str):
    sender_email = "test@example.com"
    msg = MIMEText(f"Your OTP is: {otp}")
    msg['Subject'] = 'Your OTP Code'
    msg['From'] = sender_email
    msg['To'] = to_email
    with smtplib.SMTP("localhost", 1025) as smtp:
        smtp.send_message(msg)

@router.post('/user/generate-otp/')
def generate_otp(user: user_schema.ForgetEmail, db: Session = Depends(get_db)):
    otp = str(random.randint(100000, 999999))  #
    db_otp = db.query(model.Users).filter(model.Users.email == user.email).first()
    if db_otp:
        db_otp.otp_code = otp
        db_otp.otp_created_at = datetime.utcnow()
        
        db.add(db_otp)
        db.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found")    
    
    send_otp(user.email, otp)
    return {"message": "OTP sent to your email"}    

@router.post('/user/forget-password/')
async def forget_password(forget: user_schema.ForgetPassword, db: Session = Depends(get_db)):

    db_user = db.query(model.Users).filter(model.Users.email == forget.email, model.Users.otp_code == forget.otp).first()
    if not db_user:
     raise HTTPException(status_code=404, detail="Invalid OTP or email")

    if datetime.utcnow() > db_user.otp_created_at + timedelta(minutes=1):
        db_user.otp_code = None
        db_user.otp_created_at = None
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP expired, please request a new one")   
     
    if db_user:

        db_user.password = Hash.bcrypt(forget.password)
        db_user.otp_code = None
        db_user.otp_created_at = None
        db.commit()   
               
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )     

        
    return {"message": "Password reset successful"}    
        


