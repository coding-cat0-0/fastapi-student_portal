from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from schema import admin_schema
from models import model
from authentication.oauth2 import create_access_token, get_current_user
from database.structure import get_db, engine
from typing import List
from hasher.hashing import Hash

router = APIRouter(
    tags=["For Admin"]
)

@router.post('/users')
def create_users(
    user: admin_schema.CreateUsers,
    db: Session = Depends(get_db),
    current_admin: model.Admin = Depends(get_current_user())):
    db_user = None
    role = None
    
    existing = db.query(model.Users).filter(model.Users.email == user.email.lower()).first()
    if  existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    if user.role not in ["student", "teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role specified"
        )
    if user.role == "student":    
      db_student = db.query(model.Student).filter(model.Student.email == user.email.lower()).first()
      if not db_student:
    # Student does not exist, so create a new one
        new_student = model.Student(
        name=user.name,
        email=user.email.lower(),
        password=Hash.bcrypt(user.password))
        db.add(new_student)
        db.commit()
        db.refresh(new_student)

    elif user.role == "teacher":
        print(user)
        db_teacher = db.query(model.Teacher).filter(model.Teacher.email == user.email.lower()).first()
        if not db_teacher:
            new_teacher = model.Teacher(
            name=user.name,
            course_instructor=user.instructor,
            email=user.email.lower(),
            password=Hash.bcrypt(user.password)
            )
            db.add(new_teacher)
            db.commit()       
            db.refresh(new_teacher)  
         
    elif user.role == "admin":       
        db_admin = db.query(model.Admin).filter(model.Admin.admin_email == user.email).first()
        if not db_admin:        
          new_admin = model.Admin(admin_name=user.name,admin_email=user.email.lower(), 
          admin_password=Hash.bcrypt(user.password))
          db.add(new_admin)
          db.commit()
          db.refresh(new_admin)   
        
    new_user = model.Users(name = user.name, role=user.role, email=user.email,
    password=Hash.bcrypt(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"Message" : "User created succesfully",
            "User Information" : new_user}
    
    
@router.post('/events')
def create_event(
    event: admin_schema.EventInput,
    db: Session = Depends(get_db),
    current_admin: model.Admin = Depends(get_current_user())
):
    # Logic to create an event
    new_event = model.Events(
        event_name=event.name,
        event_date=event.event_date,
        event_location=event.location
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return {"message": "Event created successfully"}

@router.post('/courses')
def create_course(
    course: admin_schema.CreateCourses,
    db: Session = Depends(get_db),
    current_admin: model.Admin = Depends(get_current_user())
):
    new_course = model.Courses(course_name = course.course_name, instructor=course.instructor,
    credit_hrs=course.credit_hrs, fee=course.fee)
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return {"message": "Course created successfully", "course": new_course}


# For admin to see student attendance
@router.get('/admin/student/attendance/{student_id}')
def view_student_attendance(
    student_id: int,
    stu_course: str,
    db: Session = Depends(get_db),
    current_admin: model.Admin = Depends(get_current_user())
):
    db_student = db.query(model.Student).filter(model.Student.id == student_id).first()
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
     
    confirmation = db.query(model.Enrollment).filter(model.Enrollment.student_id == student_id,
    model.Enrollment.course==stu_course).first()
    if not confirmation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not enrolled in this course"
        )
    
    attendance_records = db.query(model.Attendance).filter(
        model.Attendance.student_id == student_id,
        model.Attendance.course == stu_course
    ).all()
    if not attendance_records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance records not found"
        )
    return attendance_records
    
# For admin to see student grades
@router.get('/admin/student/grades/{student_id}')    
def view_student_grades(student_id: int, 
stu_course: str, db: Session = Depends(get_db),
current_admin: model.Admin = Depends(get_current_user)):
    
    db_student = db.query(model.Student).filter(model.Student.id == student_id).first()
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
        
    confirmation = db.query(model.Enrollment).filter(model.Enrollment.student_id == student_id,
    model.Enrollment.course==stu_course).first()
    if not confirmation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not enrolled in this course"
        )
        
    grade_records = db.query(model.Grade).filter(
        model.Grade.student_id == student_id,
        model.Grade.course == stu_course
    ).all()
    if not grade_records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade records not found"
        )
    return grade_records    


@router.get('/admin/users')
def view_users(db: Session = Depends(get_db)):
    users = db.query(model.Users).all()
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No users found"
        )
    return users     
@router.delete('/admin/users/{username}')
def delete_user(username: str, db : Session = Depends(get_db),
        current_admin: model.Admin = Depends(get_current_user())):
    
    db_user = db.query(model.Users).filter(model.Users.email == username).first()
    if  db_user:
        db.delete(db_user)
        db.commit()
    db_student = db.query(model.Student).filter(model.Student.email == username).first()    
    if  db_student:
        db.delete(db_student)    
        db.commit()
    
    db_teacher = db.query(model.Teacher).filter(model.Teacher.email == username).first()
    if  db_teacher:
        db.delete(db_teacher)
        db.commit()
    
    db_admin = db.query(model.Admin).filter(model.Admin.admin_email == username).first()
    if db_admin:            
        db.delete(db_admin)
        db.commit()
        
    if not any([db_user, db_student, db_teacher, db_admin]):
        raise HTTPException( status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
 
    return {"message": "User deleted successfully"}