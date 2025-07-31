from fastapi import HTTPException, status, Depends, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from typing import Annotated
from schema import stu_schema
from models import model
from database.structure import get_db
from typing import Optional
from fastapi.security import HTTPBearer



# JWT Config
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security scheme for FastAPI docs
bearer_scheme = HTTPBearer()

# Generate JWT
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) +( expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) #Creates a JWT token using the data, secret key, and algorithm.
    #The result is a long string — your access token.
    return encoded_jwt

# Decode JWT & get current websocket
async def get_current_ws(websocket : WebSocket,db:Session,required_role: Optional[str] = None):
     
    token = websocket.query_params.get("token")
    if not token:
         await websocket.close(code = status.WS_1008_POLICY_VIOLATION)
         return None
     
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        role = payload.get("role")
        #print("Decoded token payload:", payload)

        
        user = db.query(model.Users).filter(model.Users.id == user_id).first()
        if not user:    
            print("User not found in db")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return None
        
        if user.role != role:
         print("Role mismatch: Token role is", role, "but DB role is", user.role)
         await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
         return None
        
        if required_role and role != required_role:
                await websocket.close(code = status.WS_1008_POLICY_VIOLATION)
                return None

        return user
    except JWTError:
        await websocket.close(code = status.WS_1008_POLICY_VIOLATION)
        return None
