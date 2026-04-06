from flask import Blueprint, render_template
from flask_login import login_required, current_user

from ..models import Student, Attendance
from . import student_required


student_bp = Blueprint('student', __name__)


@student_bp.route('/student/dashboard')
@login_required
@student_required
def dashboard():
    account = current_user
    student = None
    if account.student_id:
        student = Student.query.get(account.student_id)
    if not student:
        student = Student.query.filter_by(
            roll_number=account.roll_number,
            class_name=account.class_name,
            section=account.section
        ).first()
        if student and not account.student_id:
            account.student_id = student.id
            from .. import db
            db.session.commit()

    attendance_records = []
    total_days = present = absent = late = 0

    if student:
        attendance_records = (
            Attendance.query.filter_by(student_id=student.id)
            .order_by(Attendance.date.desc())
            .all()
        )
        total_days = len(attendance_records)
        present = len([r for r in attendance_records if r.status == 'Present'])
        absent = len([r for r in attendance_records if r.status == 'Absent'])
        late = len([r for r in attendance_records if r.status == 'Late'])

    percent = round((present / total_days) * 100, 2) if total_days else 0

    return render_template(
        'student/dashboard.html',
        student=student,
        account=account,
        attendance_records=attendance_records,
        total_days=total_days,
        present=present,
        absent=absent,
        late=late,
        percent=percent
    )
