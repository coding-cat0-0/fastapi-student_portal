from fastapi import HTTPException, status, Depends
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

# Decode JWT & get current user
def get_current_user(required_role: Optional[str] = None):
    def inner (credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Session = Depends(get_db)
) :
     data = credentials.credentials
     credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
     )
     try:
        payload = jwt.decode(data, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        role = payload.get("role")
        if not user_id or not role:
            raise credentials_exception     
        if required_role and role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        user = db.query(model.Users).filter(model.Users.id == int(user_id)).first()

        if not user or user.role != role:
                raise credentials_exception
        if not user:
            raise credentials_exception
        return user
     except JWTError:
            raise credentials_exception
    return inner