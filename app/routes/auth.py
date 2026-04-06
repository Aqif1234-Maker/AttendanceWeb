from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user

from .. import db
from ..models import Teacher, StudentAccount


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def landing():
    return render_template('auth/landing.html')


@auth_bp.route('/teacher/signup', methods=['GET', 'POST'])
def teacher_signup():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return redirect(url_for('auth.teacher_signup'))
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.teacher_signup'))
        if Teacher.query.filter_by(email=email).first():
            flash('Email is already registered.', 'danger')
            return redirect(url_for('auth.teacher_signup'))

        teacher = Teacher(full_name=full_name, email=email)
        teacher.set_password(password)
        db.session.add(teacher)
        db.session.commit()

        flash('Account created. Please log in.', 'success')
        return redirect(url_for('auth.teacher_login'))

    return render_template('auth/teacher_signup.html')


@auth_bp.route('/teacher/login', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        teacher = Teacher.query.filter_by(email=email).first()
        if not teacher or not teacher.check_password(password):
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('auth.teacher_login'))

        login_user(teacher)
        session['user_type'] = 'teacher'
        return redirect(url_for('teacher.dashboard'))

    return render_template('auth/teacher_login.html')


@auth_bp.route('/teacher/logout')
def teacher_logout():
    logout_user()
    session.pop('user_type', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('auth.teacher_login'))


@auth_bp.route('/student/signup', methods=['GET', 'POST'])
def student_signup():
    if request.method == 'POST':
        name = request.form.get('full_name', '').strip()
        roll_number = request.form.get('roll_number', '').strip().upper()
        class_name = request.form.get('class', '').strip()
        section = request.form.get('section', '').strip().upper()
        contact = request.form.get('contact', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return redirect(url_for('auth.student_signup'))
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.student_signup'))
        if StudentAccount.query.filter_by(
            roll_number=roll_number,
            class_name=class_name,
            section=section
        ).first():
            flash('Roll number already registered for this class/section.', 'danger')
            return redirect(url_for('auth.student_signup'))

        account = StudentAccount(
            name=name,
            roll_number=roll_number,
            class_name=class_name,
            section=section,
            contact=contact
        )
        account.set_password(password)
        db.session.add(account)
        db.session.commit()

        flash('Registration submitted. Awaiting teacher approval.', 'info')
        return redirect(url_for('auth.student_login'))

    return render_template('auth/student_signup.html')


@auth_bp.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        roll_number = request.form.get('roll_number', '').strip().upper()
        password = request.form.get('password', '')

        student = StudentAccount.query.filter_by(roll_number=roll_number).first()
        if not student or not student.check_password(password):
            flash('Invalid roll number or password.', 'danger')
            return redirect(url_for('auth.student_login'))
        if not student.approved:
            flash('Your account is pending teacher approval.', 'warning')
            return redirect(url_for('auth.student_login'))

        if not student.student_id:
            from ..models import Student
            matching_student = Student.query.filter_by(roll_number=student.roll_number).first()
            if matching_student:
                student.student_id = matching_student.id
                db.session.commit()

        login_user(student)
        session['user_type'] = 'student'
        return redirect(url_for('student.dashboard'))

    return render_template('auth/student_login.html')


@auth_bp.route('/student/logout')
def student_logout():
    logout_user()
    session.pop('user_type', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('auth.student_login'))
