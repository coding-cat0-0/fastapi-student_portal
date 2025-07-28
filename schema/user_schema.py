from pydantic import BaseModel, Field, field_validator
import re

class LoginUser(BaseModel):
    email: str
    password: str        
    @field_validator('email')
    def email_must_be_valid(cls, v):    
        if not re.search(r"\w+@(\w+\.)?\w+\.(edu)$",v, re.IGNORECASE):
            raise ValueError("Invalid email format")
        else:
            return v
        
    @field_validator('password')    
    def password_must_be_strong(cls, p):
             if not re.search(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%&*^_-])[A-Za-z\d!@#$%^&_*-]{8,}$",p):
                 raise ValueError("Invalid Password")
             else:
                    return p
                
                
class ForgetPassword(BaseModel):
    email: str
    password: str            
    @field_validator('email')
    def email_must_be_valid(cls, v):    
        if not re.search(r"\w+@(\w+\.)?\w+\.(edu)$",v, re.IGNORECASE):
            raise ValueError("Invalid email format")
        else:
            return v
        
    @field_validator('password')    
    def password_must_be_strong(cls, p):
             if not re.search(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%&*^_-])[A-Za-z\d!@#$%^&_*-]{8,}$",p):
                 raise ValueError("Invalid Password")
             else:
                    return p                    