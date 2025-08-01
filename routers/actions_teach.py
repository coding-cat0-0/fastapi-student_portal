from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from schema import teacher_schema
from models import model
from authentication.oauth2 import create_access_token, get_current_user
from database.structure import get_db, engine
from typing import List
import datetime
from websockets_router.login_websocket import active_connections
import asyncio
from websockets_router.core_socketio import socket_manager
from websockets_router.celary import stu_notifications


router = APIRouter(
    tags=["For Faculty"]
)
# ATTENDANCE:

@router.post('/student/attendance/{student_id}')
async def student_attendance(student_id: int,
    teacher: teacher_schema.AttendanceInput,
    db: Session = Depends(get_db),
    current_teacher: model.Users = Depends(get_current_user())
):
    # Logic to mark attendance for a student

    db_course = db.query(model.Enrollment).filter(model.Enrollment.student_id == student_id,model.Enrollment.course == teacher.course).first()
    if not db_course:
         raise HTTPException(
             status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not enrolled in this course")
           
    mark_attendance = model.Attendance( student_id=student_id, student_name= teacher.student_name ,course=teacher.course, 
    date=teacher.attendance_date, present=teacher.present)
    db.add(mark_attendance)
    db.commit()
    db.refresh(mark_attendance)
    
    #print("Active connections:", active_connections)
    #print("Current teacher:", current_teacher.email)
    if current_teacher.email in active_connections:
        asyncio.create_task(
            send_notification(
                current_teacher.email,
                "Attendance marked successfully"
            )
        )
    student = db.query(model.Users).filter(model.Users.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")    
    
    stu_notifications.delay(student.email, "Your attendance has been posted")
    
    return {"message": "Attendance marked successfully"}

async   def send_notification(email:str, message:str):
    #print(f"Sending notification to {email}: {message}")
    if email in active_connections:
        await active_connections[email].send_json({
            "type": "event_created",
            "message": message
        }) 


# GRADES:
@router.post('/student/grades/{student_id}')
async def student_grades(student_id: int,st_course: str,
    teacher: teacher_schema.GradeInput,
    db: Session = Depends(get_db),
    current_teacher: model.Users = Depends(get_current_user())
):
    
    # Logic to add grades for a student
    db_student = db.query(model.Enrollment).filter(model.Enrollment.student_id == student_id, model.Enrollment.course == st_course).first()
    if not db_student:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not enrolled in this course"
        )
       
    total_obtained = teacher.quiz + teacher.assignment + teacher.midterm + teacher.finalterm
    total_possible = teacher.total_quiz + teacher.total_assignment + teacher.total_midterm + teacher.final_total

    final_grade = (total_obtained / total_possible) * 100
    if final_grade >= 90:
        grade = "A"
    elif final_grade >= 80:
        grade = "B"
    elif final_grade >= 70:
       grade = "C"
    elif final_grade >= 60:
      grade = "D"
    else:
       grade = "F"    

    new_grade = model.Grade(
    student_id=student_id,
    student_name=teacher.student_name,
    course=st_course,
    quiz=teacher.quiz,
    total_quizmarks=teacher.total_quiz,
    assignment=teacher.assignment,
    total_assignmentmarks=teacher.total_assignment,
    midterm=teacher.midterm,
    total_midterm=teacher.total_midterm,
    finalterm=teacher.finalterm,
    final_total=teacher.final_total,
    grade=grade)
    
    db.add(new_grade)
    db.commit()
    db.refresh(new_grade)
    
    if current_teacher.email in active_connections:
        asyncio.create_task(
            send_notification(
                current_teacher.email,
                "Grades uploaded successfully"
            )
        )
    
    return {"message": "Grades added successfully"}

async  def send_notification(email:str, message:str):
    #print(f"Sending notification to {email}: {message}")
    if email in active_connections:
        await active_connections[email].send_json({
            "type": "event_created",
            "message": message
        }) 

@router.post('/student/tasks/{course_id}')
async def upload_tasks(course_id: int,
    task: teacher_schema.UploadTask,
    db: Session = Depends(get_db),
    current_teacher: model.Users = Depends(get_current_user())
):
    
    db_course = db.query(model.Courses).filter(model.Courses.id == course_id).first()
    if not db_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    upload_date = datetime.date.today()
    new_task = model.Tasks(
        task_name=task.task_name,
        upload_date=upload_date,
        due_date=task.due_date,
        course_id=course_id
    )
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    if current_teacher.email in active_connections:
        asyncio.create_task(
            send_notification(
                current_teacher.email,
                "Task uploaded successfully"
            )
        )
    
    return {"message": "Task uploaded successfully", "task": new_task}

async   def send_notification(email:str, message:str):
    #print(f"Sending notification to {email}: {message}")
    if email in active_connections:
        await active_connections[email].send_json({
            "type": "event_created",
            "message": message
        }) 