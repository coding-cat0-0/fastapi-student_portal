from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float, DateTime
from database.structure import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Date
from datetime import datetime


class Users(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # nullable=False ensures that the name cannot be null
    role = Column(String, nullable=False)  # e.g., "student", "teacher", "admin"
    instructor = Column(String, nullable=True)  # Optional for students
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  # Password should be hashed in practice
    otp_code = Column(String, nullable=True)  # Optional field for OTP code
    otp_created_at = Column(DateTime, nullable=True) 

class Teacher(Base):
    __tablename__ = "teachers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False) # nullable=False ensures that the name cannot be null
    course_instructor = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  
    students = relationship("Student", back_populates="teacher")

    
class Attendance(Base):    
    __tablename__ = "attendance_records"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    student_name = Column(String,nullable=False)  
    course = Column(String, nullable=False)  # or course_id if you have a courses table
    date = Column(Date, nullable=False)    # or use Date type if you want
    present = Column(Boolean, default=False)  # default to False if not specified    
    student = relationship("Student", back_populates="attendance_records",foreign_keys=[student_id])
    # last_name = Column(String, nullable=True)   

class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    admin_name = Column(String, nullable=False)
    admin_email = Column(String, unique=True, nullable=False)
    admin_password = Column(String, nullable=False)
    
class Grade(Base):
    __tablename__ = "grades"
    id = Column(Integer, primary_key=True, index=True)    
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    student_name = Column(String,nullable=False) 
    course = Column(String, nullable=False) 
    quiz = Column(Float, nullable=False)
    total_quizmarks = Column(Float, nullable=False)
    assignment = Column(Float, nullable=False)
    total_assignmentmarks = Column(Float, nullable=False)
    midterm = Column(Float, nullable=False)
    total_midterm = Column(Float, nullable=False)
    finalterm = Column(Float, nullable=False)
    final_total = Column(Float, nullable=False) 
    grade = Column(String, nullable=False)  
    student = relationship("Student", back_populates="grades", foreign_keys=[student_id])
    
class Enrollment(Base):        
    __tablename__ = "course_enrollments"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    student_name = Column(String, nullable=False)
    course = Column(String, nullable=False)  
    student = relationship("Student", back_populates="enrollments", foreign_keys=[student_id])

class Student(Base):    
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True,nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    teacher = relationship("Teacher", back_populates="students")
    attendance_records = relationship("Attendance", back_populates="student",foreign_keys=[Attendance.student_id])
    grades = relationship("Grade", back_populates="student",foreign_keys=[Grade.student_id])    
    enrollments = relationship("Enrollment", back_populates="student", foreign_keys=[Enrollment.student_id])


class Events(Base):
        __tablename__ = "events"
        id = Column(Integer, primary_key=True, index=True)
        event_name = Column(String, nullable=False)
        event_date = Column(Date, nullable=False)
        event_location = Column(String, nullable=False)
        
        
class Courses(Base):        
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String, unique=True, nullable=False)
    instructor = Column(String, nullable=False) 
    credit_hrs = Column(Integer, nullable=False)
    fee = Column(Float, nullable=False)
    

class Tasks(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String, nullable=False)
    task_description = Column(String, nullable=True)
    upload_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"))
    course = relationship("Courses", backref="tasks")
    
class UploadTasks(Base):
    __tablename__ = "upload_tasks"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    upload_date = Column(Date, nullable=False)
    task = relationship("Tasks", backref="upload_tasks")
    student = relationship("Student", backref="upload_tasks")    