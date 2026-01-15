from flask import Blueprint, render_template, session, redirect, url_for
from .models import Student, Attendance
from .utils import login_required

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    if 'user_id' in session:
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
def prof_dashboard():
    if 'user_id' not in session or session.get('role') != 'professor':
        return redirect(url_for('auth.login'))

    prof = Professor.query.filter_by(prof_id=session['user_id']).first()
    return render_template('admin/prof.html', prof=prof)
