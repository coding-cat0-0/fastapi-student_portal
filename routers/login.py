from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from schema import user_schema
from models import model
from authentication.oauth2 import create_access_token, get_current_user
from database.structure import get_db, engine
from hasher.hashing import Hash, pwd_context
from typing import List

router = APIRouter(
    tags=["Authentication"]
)



@router.post('/user/login')
def login( user: user_schema.LoginUser,
    db: Session = Depends(get_db)):  
    db_user = None
    role = None
    
    db_student = db.query(model.Student).filter(model.Student.email == user.email).first()
    if db_student and Hash.verify_password(user.password, db_student.password):
        db_user = db_student
        role = "student"
    
    db_teacher = db.query(model.Teacher).filter(model.Teacher.email == user.email).first()
    if db_teacher and Hash.verify_password(user.password, db_teacher.password):
        db_user = db_teacher
        role = "teacher"    
        
    db_admin = db.query(model.Admin).filter(model.Admin.admin_email == user.email).first()
    if db_admin and Hash.verify_password(user.password, db_admin.admin_password):
        db_user = db_admin
        role = "admin" 
        
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )       
    
    access_token = create_access_token(data={"role":role,"sub": str(db_user.id)})
    return {"access_token": access_token, "token_type": "bearer", "role": role}




@router.post('/user/forget-password/')
def forget_password(forget: user_schema.ForgetPassword, db: Session = Depends(get_db)):

    
    db_student = db.query(model.Student).filter(model.Student.email == forget.email).first()
    if db_student:
        db_student.password = Hash.bcrypt(forget.password)
        db.commit()
        return {"message": "Password updated successfully for student"}
  

    db_teacher = db.query(model.Teacher).filter(model.Teacher.email == forget.email).first()
    if db_teacher:
        db_teacher.password = Hash.bcrypt(forget.password)
        db.commit()
        return {"message": "Password updated successfully for teacher"}

    db_admin = db.query(model.Admin).filter(model.Admin.admin_email == forget.email).first()
    if db_admin :
       db_admin.admin_password = Hash.bcrypt(forget.password)
       db.commit()
       return {"message": "Password updated successfully for admin"}

       
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )     
'''
@router.post('/student/signup')
def student_signup( student: stu_schema.SignupStudent,
    db: Session = Depends(get_db)
):
    existing = db.query(model.Student).filter(model.Student.email == student.email.lower()).first()
    if  existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    new_student = model.Student(name=student.name,email=student.email.lower(),
    password=Hash.bcrypt(student.password))
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return {"Student Information" : new_student, 
            "message": "Student created successfully"
            }
'''

