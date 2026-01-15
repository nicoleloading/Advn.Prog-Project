from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user_table'
    student_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='student')  # Add this line
    
    student = db.relationship('Student', backref='user', uselist=False)

class Student(db.Model):
    __tablename__ = 'student_table'
    student_id = db.Column(db.String(50), db.ForeignKey('user_table.student_id'), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    program = db.Column(db.String(100))
    year = db.Column(db.Integer)
    
    attendances = db.relationship('Attendance', backref='student', lazy=True)

class Professor(db.Model):
    __tablename__ = 'professor_table'
    prof_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    course = db.Column(db.String(100))
    course_id = db.Column(db.String(50))
    schedule = db.Column(db.String(100))
    
    classes = db.relationship('Class', backref='prof', lazy=True)

class Class(db.Model):
    __tablename__ = 'class_table'
    course_id = db.Column(db.String(50), primary_key=True)
    professor_name = db.Column(db.String(100))
    schedule = db.Column(db.String(100))
    course = db.Column(db.String(100))
    prof_id = db.Column(db.String(50), db.ForeignKey('professor_table.prof_id'))
    
    attendances = db.relationship('Attendance', backref='class_ref', lazy=True)

class Attendance(db.Model):
    __tablename__ = 'attendance_table'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.String(50), db.ForeignKey('student_table.student_id'), nullable=False)
    course_id = db.Column(db.String(50), db.ForeignKey('class_table.course_id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Present')
