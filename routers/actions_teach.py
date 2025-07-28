from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from schema import teacher_schema
from models import model
from authentication.oauth2 import create_access_token, get_current_user
from database.structure import get_db, engine
from typing import List
import datetime

router = APIRouter(
    tags=["For Faculty"]
)
# ATTENDANCE:
@router.post('/student/attendance/{teacher_id}/{student_id}')
def student_attendance(teacher_id:int,student_id: int,
    teacher: teacher_schema.AttendanceInput,
    db: Session = Depends(get_db),
    current_teacher: model.Teacher = Depends(get_current_user())
):
    # Logic to mark attendance for a student
    if current_teacher.id != teacher_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Wrong ID entered")
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
    return {"message": "Attendance marked successfully"}

# GRADES:
@router.post('/student/grades/{teacher_id}/{student_id}')
def student_grades(teacher_id:int,student_id: int,st_course: str,
    teacher: teacher_schema.GradeInput,
    db: Session = Depends(get_db),
    current_teacher: model.Teacher = Depends(get_current_user())
):
    
    if current_teacher.id != teacher_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Wrong ID entered")
    
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
    return {"message": "Grades added successfully"}

@router.post('/student/tasks/{teacher_id}/{course_id}')
def upload_tasks(teacher_id: int, course_id: int,
    task: teacher_schema.UploadTask,
    db: Session = Depends(get_db),
    current_teacher: model.Teacher = Depends(get_current_user())
):
    if current_teacher.id != teacher_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Wrong ID entered")
    
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
    
    return {"message": "Task uploaded successfully", "task": new_task}
