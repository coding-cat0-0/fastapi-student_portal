from pydantic import BaseModel, Field, field_validator
import re
from datetime import date

class Teachers(BaseModel):
    
    name: str
    course: str
    email: str
    password: str   
    class Config():
        orm_mode = True
        

        
class LoginTeacher(BaseModel):
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

class SignupTeachers(Teachers):
     name: str   
     course: str
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
        

class AttendanceInput(BaseModel):
    student_name: str
    course: str  # or course_id: int if you have a courses table
    attendance_date: date = Field(default_factory=date.today)  # from datetime import date
    present: bool
    
class GradeInput(BaseModel):
    student_name: str
    quiz: float
    total_quiz: float
    assignment: float
    total_assignment: float
    midterm: float
    total_midterm: float
    finalterm: float
    final_total: float

class UploadTask(BaseModel):
    task_name: str
    due_date: date = Field(default_factory=date.today)


