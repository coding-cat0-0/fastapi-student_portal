from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from schema import stu_schema
from models import model
from authentication.oauth2 import create_access_token, get_current_user
from database.structure import get_db, engine
from typing import List
import datetime

router = APIRouter(
        tags=["For Students"]
)

# GET ATTENDANCE:

@router.get('/student/attendance/{student_id}/{st_course}')
def view_attendance(student_id: int,st_course:str,
    db: Session = Depends(get_db),
    current_student: model.Student = Depends(get_current_user())
):
    # To check if the student is the one requesting their grades
    if current_student.id != student_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Incorrect student ID")

    db_student = db.query(model.Enrollment).filter(model.Enrollment.student_id == student_id, model.Enrollment.course == st_course).first()
    if not db_student:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found enrolled in this course"
        )    
    attendance_records = db.query(model.Attendance).filter(model.Attendance.student_id == student_id,
        model.Attendance.course == st_course ).all()
    if not attendance_records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance records not found"
        )    
    unique_attendance = {}
    for record in attendance_records:
        unique_attendance[record.date] = record  # Overwrites duplicates

    return list(unique_attendance.values())

# GET GRADES:
@router.get('/student/grades/{student_id}')
def view_grades(student_id: int,st_course: str,
    db: Session = Depends(get_db),
    current_student: model.Student = Depends(get_current_user())
):
    # To check if the student is the one requesting their grades
    if current_student.id != student_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Incorrect student ID")
    
    db_enrollment = db.query(model.Enrollment).filter(model.Enrollment.student_id == student_id,
    model.Enrollment.course == st_course).first()
    if not db_enrollment:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found enrolled in this course"
        )    
    
    grade_records = db.query(model.Grade).filter(model.Grade.student_id == student_id,
        model.Grade.course == st_course ).first()
    if not grade_records:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Grade records not found")
    else:    

        return grade_records
    
# GET TASKS:

@router.get('/student/tasks/{student_id}')    
def see_tasks(student_id:int, db:Session=Depends(get_db),
    current_student: model.Student = Depends(get_current_user())):
    
    if current_student.id != student_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
        detail="Incorrect student ID")
     
    get_tasks = db.query(model.Tasks).all()
    if not get_tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tasks found"
        )
    return {"Tasks": get_tasks}    

@router.post('/student/upload/tasks/{student_id}/{task_id}')
def upload_task(student_id: int,task_id:int,
    db: Session = Depends(get_db),
    current_student: model.Student = Depends(get_current_user())):
    
    if current_student.id != student_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
        detail="Incorrect student ID")
    
    db_check_task = db.query(model.Tasks).filter(model.Tasks.id == task_id).first()
    if not db_check_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
    task = db.query(model.Tasks).filter(model.Tasks.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
   
    if datetime.date.today() > task.due_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task submission is past the deadline"
        )
    else:
     db_task = model.UploadTasks(student_id = student_id, task_id = task_id,
     upload_date = datetime.date.today())          
     db.add(db_task)
     db.commit()
     db.refresh(db_task)   
       
     return {"message": "Task uploaded successfully"}

# See courses:    
@router.get('/courses/{st_id}')
def see_your_course(st_id:int, db: Session = Depends(get_db)):
    enrolled_course = db.query(model.Enrollment).filter(model.Enrollment.student_id == st_id).all()
    if not enrolled_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not enrolled in any course. Please enroll in a course first."
        )
    course = [enrolled.course for enrolled in enrolled_course] #for items (enrolled) in enrolled_course(list)
    # loop over each item and get course object i.e enrolled.course   
    return { "Your Courses" : course}
       

# Enroll in a course:
@router.post('/courses/{course_name}/{st_name}')
def create_course(course_name: str,st_name :str, db: Session = Depends(get_db),
        current_student: model.Student = Depends(get_current_user())):
    
    deb_course = db.query(model.Courses).filter(model.Courses.course_name == course_name).first()
    if not deb_course:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    
    existing_enrollment = db.query(model.Enrollment).filter(model.Enrollment.student_id == current_student.id, 
    model.Enrollment.course == course_name).first()
    
    if existing_enrollment:     
        raise HTTPException(status_code=status.HTTP_302_FOUND, detail="You are already enrolled in this course")
    else:
        new_enrollment = model.Enrollment(student_id=current_student.id, student_name=st_name,course=course_name)
        db.add(new_enrollment)
        db.commit()
        db.refresh(new_enrollment)
        return {"message": "Enrollment successful", "course": new_enrollment.course}
    
# View all courses the uni is offering:    
@router.get('/courses')
def view_courses(db: Session = Depends(get_db)):
    courses = db.query(model.Courses).all()
    if not courses:
        raise HTTPException( status_code=status.HTTP_404_NOT_FOUND, 
            detail="No courses available")
        
    return {"Available Courses" :courses}    

# See upcoming events:       
@router.get('/events')
def get_events(db: Session = Depends(get_db)):
    # Logic to get events for a student
    events = db.query(model.Events).all()
    if not events:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No upcoming events found"
        )
    return events
