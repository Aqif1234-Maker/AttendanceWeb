from functools import wraps
from flask import session, redirect, url_for, flash, request, jsonify
from flask_login import current_user


def teacher_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or session.get('user_type') != 'teacher':
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Unauthorized'}), 401
            flash('Please login as a teacher to continue.', 'warning')
            return redirect(url_for('auth.teacher_login'))
        return view_func(*args, **kwargs)
    return wrapper


def student_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or session.get('user_type') != 'student':
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Unauthorized'}), 401
            flash('Please login as a student to continue.', 'warning')
            return redirect(url_for('auth.student_login'))
        return view_func(*args, **kwargs)
    return wrapper
