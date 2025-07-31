from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from schema import admin_schema
from models import model
from authentication.oauth2 import create_access_token, get_current_user
from database.structure import get_db, engine
from typing import List
from hasher.hashing import Hash
from websockets_router.login_websocket import active_connections
import asyncio

router = APIRouter(
    tags=["For Admin"]
)

@router.post('/users')
async def create_users(
    user: admin_schema.CreateUsers,    
    db: Session = Depends(get_db),
    current_admin: model.Users = Depends(get_current_user())):
    db_user = None
    role = None
    
    if current_admin.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can perform this action")
    
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

    new_user = model.Users(name = user.name, role=user.role, email=user.email,
    password=Hash.bcrypt(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    if current_admin.email in active_connections:
        asyncio.create_task(
            send_notification(
            current_admin.email,
            f"New user with role {new_user.role} created successfully"
        ))

    return {"Message" : "User created succesfully",
            "User Information" : new_user}

async   def send_notification(email:str, message:str):
    if email in active_connections:
        await active_connections[email].send_json({
            "type": "event_created",
            "message": message
        }) 
    
@router.post('/events')
async def create_event(
    event: admin_schema.EventInput,
    db: Session = Depends(get_db),
    current_admin: model.Users = Depends(get_current_user())
):
    # Logic to create an event
    if current_admin.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can perform this action")
    
    new_event = model.Events(
        event_name=event.name,
        event_date=event.event_date,
        event_location=event.location
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    
    if current_admin.email in active_connections:
         asyncio.create_task(
            send_notification(
            current_admin.email,
            f"New event created successfully"
        ))

    
    return {"message": "Event created successfully"}

async  def send_notification(email:str, message:str):
    if email in active_connections:
        await active_connections[email].send_json({
            "type": "event_created",
            "message": message
        }) 

@router.post('/courses')
async def create_course(
    course: admin_schema.CreateCourses,
    db: Session = Depends(get_db),
    current_admin: model.Users = Depends(get_current_user())
):
  
    if current_admin.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can perform this action")
    
    new_course = model.Courses(course_name = course.course_name, instructor=course.instructor,
    credit_hrs=course.credit_hrs, fee=course.fee)
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    
    if current_admin.email in active_connections:
  
         asyncio.create_task(
            send_notification(
            current_admin.email,
            f"New course created successfully"
        ))
    return {"message": "Course created successfully"}

async  def send_notification(email:str, message:str):
    if email in active_connections:
        await active_connections[email].send_json({
            "type": "event_created",
            "message": message
        }) 

# For admin to see student attendance
@router.get('/admin/student/attendance/{student_id}')
def view_student_attendance(
    student_id: int,
    stu_course: str,
    db: Session = Depends(get_db),
    current_admin: model.Users = Depends(get_current_user())
):  
    
    if current_admin.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can perform this action") 
    
    db_student = db.query(model.Users).filter(model.Users.id == student_id).first()
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
current_admin: model.Users = Depends(get_current_user)):
    
    if current_admin.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can perform this action")
   
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
def view_users(db: Session = Depends(get_db), current_admin: model.Users = Depends(get_current_user())):
    
    if current_admin.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can perform this action")
    
    users = db.query(model.Users).all()
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No users found"
        )
    return users     
@router.delete('/admin/users/{username}')
def delete_user(username: str, db : Session = Depends(get_db),
        current_admin: model.Users = Depends(get_current_user())):
    
    if current_admin.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can perform this action")
    
    db_user = db.query(model.Users).filter(model.Users.email == username).first()
    if not db_user:
        raise HTTPException( status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    #if not any([db_user, db_student, db_teacher, db_admin]):
    return {"message": "User deleted successfully"}