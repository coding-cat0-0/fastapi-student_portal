from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Hash():
    def bcrypt(password:str):
        return pwd_context.hash(password) 
        
    def verify_password(login_password, hashed_password):
        return pwd_context.verify(login_password, hashed_password) 