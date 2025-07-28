from pydantic import BaseModel, Field, field_validator
import re
from datetime import date
from schema.teacher_schema import AttendanceInput, GradeInput
from typing import Optional
class Admin(BaseModel):
    name: str
    email: str
    password: str   
    class Config():
        orm_mode = True        

    
class LoginAdmin(BaseModel):
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

                                
class EventInput(BaseModel):                
    name : str
    event_date : date = Field(default_factory=date.today)  
    location: str
       
class ViewAttendance(AttendanceInput):
    student_id: int
    course: str
    class Config():
        orm_mode = True
    
class ViewGrade(GradeInput):
    student_id: int
    course: str
    class Config():
        orm_mode = True    
        
        
class CreateCourses(BaseModel):
    course_name: str
    instructor: str
    credit_hrs: int
    fee: float            
    class Config():
        orm_mode = True
        
class CreateUsers(BaseModel):
    name:str
    role:str
    instructor: str# Optional for students
    email:str
    password:str
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
                
                
       