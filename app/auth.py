from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User, Student, Professor

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            if user.role != role:
                flash(f'Invalid credentials for {role} login', 'danger')
                return redirect(url_for('auth.login'))
            
            session['user_id'] = user.student_id
            session['role'] = user.role

            flash('Login successful!', 'success')

            if user.role == 'professor':
                return redirect(url_for('main.prof_dashboard'))
            else:
                return redirect(url_for('main.dashboard'))

        flash('Invalid email or password', 'danger')

    return render_template('login.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        role = request.form.get('role')
        password = request.form.get('password')
        
        if role == 'student':
            student_id = request.form.get('student_id')
            name = request.form.get('name')
            email = request.form.get('email')
            program = request.form.get('program')
            year = request.form.get('year')
            
            if User.query.filter_by(email=email).first():
                flash('Email already exists', 'danger')
                return redirect(url_for('auth.register'))
            
            if User.query.filter_by(student_id=student_id).first():
                flash('Student ID already exists', 'danger')
                return redirect(url_for('auth.register'))
            
            hashed_password = generate_password_hash(password)
            
            new_user = User(student_id=student_id, name=name, email=email, password=hashed_password, role='student')
            new_student = Student(student_id=student_id, name=name, program=program, year=int(year))
            
            db.session.add(new_user)
            db.session.add(new_student)
            db.session.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        
        elif role == 'professor':
            prof_id = request.form.get('prof_id')
            name = request.form.get('prof_name')
            email = request.form.get('prof_email')
            course = request.form.get('course')
            course_id = request.form.get('course_id')
            schedule = request.form.get('schedule')
            
            if User.query.filter_by(email=email).first():
                flash('Email already exists', 'danger')
                return redirect(url_for('auth.register'))
            
            if User.query.filter_by(student_id=prof_id).first():
                flash('Professor ID already exists', 'danger')
                return redirect(url_for('auth.register'))
            
            hashed_password = generate_password_hash(password)
            
            # Use prof_id as student_id in User table (since student_id is the primary key)
            new_user = User(student_id=prof_id, name=name, email=email, password=hashed_password, role='professor')
            new_professor = Professor(prof_id=prof_id, name=name, course=course, course_id=course_id, schedule=schedule)
            
            db.session.add(new_user)
            db.session.add(new_professor)
            db.session.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('auth.login'))