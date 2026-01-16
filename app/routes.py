from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from .models import Student, Attendance, Professor, Class, db
from .utils import login_required
from datetime import datetime

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'professor':
            return redirect(url_for('main.prof_dashboard'))
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@bp.route('/dashboard')
@login_required
def dashboard():
    student = Student.query.get(session['user_id'])
    attendances = Attendance.query.filter_by(student_id=session['user_id']).order_by(Attendance.date.desc()).all()
    
    total_attendances = len(attendances)
    present_count = len([a for a in attendances if a.status == 'Present'])
    absent_count = len([a for a in attendances if a.status == 'Absent'])
    attendance_rate = round((present_count / total_attendances * 100) if total_attendances > 0 else 0, 1)
    
    return render_template('dashboard.html',
                         student=student,
                         attendances=attendances,
                         total_attendances=total_attendances,
                         present_count=present_count,
                         absent_count=absent_count,
                         attendance_rate=attendance_rate)

@bp.route('/prof/dashboard')
@login_required
def prof_dashboard():
    if session.get('role') != 'professor':
        flash('Access denied. Professors only.', 'danger')
        return redirect(url_for('auth.login'))

    prof = Professor.query.filter_by(prof_id=session['user_id']).first()
    
    if not prof:
        flash('Professor profile not found', 'danger')
        return redirect(url_for('auth.login'))
    
    # Get the class for this professor using prof.course_id
    class_info = Class.query.filter_by(course_id=prof.course_id).first()
    
    # If no class exists, create one for the professor
    if not class_info:
        class_info = Class(
            course_id=prof.course_id,
            professor_name=prof.name,
            schedule=prof.schedule,
            course=prof.course,
            prof_id=prof.prof_id
        )
        db.session.add(class_info)
        db.session.commit()
    
    # Get all students and their attendance for this course
    enrolled_students = []
    if class_info:
        attendances = Attendance.query.filter_by(course_id=class_info.course_id).all()
        student_ids = set([a.student_id for a in attendances])
        
        for student_id in student_ids:
            student = Student.query.get(student_id)
            if student:
                student_attendances = [a for a in attendances if a.student_id == student_id]
                total = len(student_attendances)
                present = len([a for a in student_attendances if a.status == 'Present'])
                rate = round((present / total * 100) if total > 0 else 0, 1)
                
                enrolled_students.append({
                    'student': student,
                    'total': total,
                    'present': present,
                    'absent': total - present,
                    'rate': rate
                })
    
    today = datetime.utcnow().strftime('%Y-%m-%d')
    return render_template('prof/prof.html', prof=prof, class_info=class_info, enrolled_students=enrolled_students, today=today)

@bp.route('/prof/enroll_student', methods=['POST'])
@login_required
def enroll_student():
    if session.get('role') != 'professor':
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))
    
    student_id = request.form.get('student_id')
    prof = Professor.query.filter_by(prof_id=session['user_id']).first()
    
    if not prof:
        flash('Professor profile not found', 'danger')
        return redirect(url_for('main.prof_dashboard'))
    
    # Get or create class
    class_info = Class.query.filter_by(course_id=prof.course_id).first()
    if not class_info:
        class_info = Class(
            course_id=prof.course_id,
            professor_name=prof.name,
            schedule=prof.schedule,
            course=prof.course,
            prof_id=prof.prof_id
        )
        db.session.add(class_info)
        db.session.commit()
    
    # Check if student exists
    student = Student.query.get(student_id)
    if not student:
        flash('Student ID not found', 'danger')
        return redirect(url_for('main.prof_dashboard'))
    
    # Check if already enrolled (has attendance record)
    existing = Attendance.query.filter_by(student_id=student_id, course_id=class_info.course_id).first()
    if existing:
        flash('Student already enrolled in this course', 'warning')
        return redirect(url_for('main.prof_dashboard'))
    
    # Create initial attendance record to enroll student
    new_attendance = Attendance(
        student_id=student_id,
        course_id=class_info.course_id,
        date=datetime.utcnow(),
        status='Present'
    )
    db.session.add(new_attendance)
    db.session.commit()
    
    flash(f'Student {student.name} enrolled successfully!', 'success')
    return redirect(url_for('main.prof_dashboard'))

@bp.route('/prof/add_attendance', methods=['POST'])
@login_required
def add_attendance():
    if session.get('role') != 'professor':
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))
    
    student_id = request.form.get('student_id')
    status = request.form.get('status')
    date_str = request.form.get('date')
    
    prof = Professor.query.filter_by(prof_id=session['user_id']).first()
    if not prof:
        flash('Professor profile not found', 'danger')
        return redirect(url_for('main.prof_dashboard'))
    
    class_info = Class.query.filter_by(course_id=prof.course_id).first()
    if not class_info:
        flash('Class not found', 'danger')
        return redirect(url_for('main.prof_dashboard'))
    
    # Validate student
    student = Student.query.get(student_id)
    if not student:
        flash('Student not found', 'danger')
        return redirect(url_for('main.prof_dashboard'))
    
    # Parse date
    try:
        attendance_date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.utcnow()
    except:
        attendance_date = datetime.utcnow()
    
    new_attendance = Attendance(
        student_id=student_id,
        course_id=class_info.course_id,
        date=attendance_date,
        status=status
    )
    db.session.add(new_attendance)
    db.session.commit()
    
    flash(f'Attendance added for {student.name}', 'success')
    return redirect(url_for('main.prof_dashboard'))

@bp.route('/prof/remove_student/<student_id>', methods=['POST'])
@login_required
def remove_student(student_id):
    if session.get('role') != 'professor':
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))
    
    prof = Professor.query.filter_by(prof_id=session['user_id']).first()
    if not prof:
        flash('Professor profile not found', 'danger')
        return redirect(url_for('main.prof_dashboard'))
    
    class_info = Class.query.filter_by(course_id=prof.course_id).first()
    if not class_info:
        flash('Class not found', 'danger')
        return redirect(url_for('main.prof_dashboard'))
    
    # Delete all attendance records for this student in this course
    deleted_count = Attendance.query.filter_by(student_id=student_id, course_id=class_info.course_id).delete()
    db.session.commit()
    
    if deleted_count > 0:
        flash('Student removed from course', 'success')
    else:
        flash('Student not found in this course', 'warning')
    
    return redirect(url_for('main.prof_dashboard'))