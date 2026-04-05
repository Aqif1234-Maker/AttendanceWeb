from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
import io
from openpyxl import Workbook

from .. import db
from ..models import Student, Attendance, StudentAccount
from . import teacher_required


teacher_bp = Blueprint('teacher', __name__)


def _class_options():
    return [str(i) for i in range(1, 13)]


def _section_options():
    return ['A', 'B', 'C', 'D']


@teacher_bp.route('/teacher/dashboard')
@login_required
@teacher_required
def dashboard():
    today = date.today()

    total_students = Student.query.count()
    today_present = Attendance.query.filter_by(date=today, status='Present').count()
    today_absent = Attendance.query.filter_by(date=today, status='Absent').count()
    today_late = Attendance.query.filter_by(date=today, status='Late').count()
    attendance_percent = round((today_present / total_students) * 100, 2) if total_students else 0

    section_pairs = (
        db.session.query(Student.class_name, Student.section)
        .distinct()
        .order_by(Student.class_name, Student.section)
        .all()
    )
    class_options = sorted({cls for cls, _ in section_pairs})
    section_options = sorted({sec for _, sec in section_pairs})

    recent_records = (
        db.session.query(Attendance, Student)
        .join(Student, Attendance.student_id == Student.id)
        .order_by(Attendance.date.desc(), Attendance.id.desc())
        .limit(10)
        .all()
    )

    return render_template(
        'teacher/dashboard.html',
        total_students=total_students,
        today_present=today_present,
        today_absent=today_absent,
        today_late=today_late,
        attendance_percent=attendance_percent,
        class_options=class_options,
        section_options=section_options,
        recent_records=recent_records
    )


@teacher_bp.route('/teacher/students', methods=['GET', 'POST'])
@login_required
@teacher_required
def students():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        name = request.form.get('name', '').strip()
        roll_number = request.form.get('roll_number', '').strip().upper()
        class_name = request.form.get('class', '').strip()
        section = request.form.get('section', '').strip().upper()
        contact = request.form.get('contact', '').strip()

        if student_id:
            student = Student.query.get(int(student_id))
            if not student:
                flash('Student not found.', 'danger')
                return redirect(url_for('teacher.students'))
            student.name = name
            student.roll_number = roll_number
            student.class_name = class_name
            student.section = section
            student.contact = contact
            db.session.commit()
            flash('Student updated successfully.', 'success')
        else:
            if Student.query.filter_by(roll_number=roll_number).first():
                flash('Roll number already exists.', 'danger')
                return redirect(url_for('teacher.students'))
            student = Student(
                name=name,
                roll_number=roll_number,
                class_name=class_name,
                section=section,
                contact=contact
            )
            db.session.add(student)
            db.session.commit()
            flash('Student added successfully.', 'success')

        return redirect(url_for('teacher.students'))

    students_list = Student.query.order_by(Student.id.desc()).all()

    return render_template(
        'teacher/students.html',
        students=students_list,
        class_options=_class_options(),
        section_options=_section_options()
    )


@teacher_bp.route('/teacher/students/delete/<int:student_id>', methods=['POST'])
@login_required
@teacher_required
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted successfully.', 'success')
    return redirect(url_for('teacher.students'))


@teacher_bp.route('/teacher/attendance')
@login_required
@teacher_required
def attendance():
    return render_template(
        'teacher/attendance.html',
        class_options=_class_options(),
        section_options=_section_options()
    )


@teacher_bp.route('/teacher/reports')
@login_required
@teacher_required
def reports():
    return render_template('teacher/reports.html')


@teacher_bp.route('/teacher/reports/export')
@login_required
@teacher_required
def reports_export():
    name = request.args.get('name', '').strip()
    class_name = request.args.get('class', '').strip()
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    def parse_date(value):
        if not value:
            return None
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None

    date_from = parse_date(date_from)
    date_to = parse_date(date_to)

    query = db.session.query(Attendance, Student).join(Student)

    if name:
        query = query.filter(Student.name.ilike(f'%{name}%'))
    if class_name:
        query = query.filter(Student.class_name == class_name)
    if date_from:
        query = query.filter(Attendance.date >= date_from)
    if date_to:
        query = query.filter(Attendance.date <= date_to)

    records = query.order_by(Attendance.date.desc()).all()

    wb = Workbook()
    ws = wb.active
    ws.title = 'Attendance Report'
    ws.append(['Name', 'Roll No', 'Class', 'Section', 'Date', 'Status'])

    for att, student in records:
        ws.append([
            student.name,
            student.roll_number,
            student.class_name,
            student.section,
            att.date.strftime('%Y-%m-%d'),
            att.status
        ])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name='attendance_report.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@teacher_bp.route('/teacher/approvals')
@login_required
@teacher_required
def approvals():
    pending_accounts = StudentAccount.query.filter_by(approved=False).order_by(StudentAccount.created_at.desc()).all()
    return render_template('teacher/approvals.html', pending_accounts=pending_accounts)


@teacher_bp.route('/teacher/approvals/approve/<int:account_id>', methods=['POST'])
@login_required
@teacher_required
def approve_account(account_id):
    account = StudentAccount.query.get_or_404(account_id)
    account.approved = True

    matching_student = Student.query.filter_by(roll_number=account.roll_number).first()
    if matching_student:
        account.student_id = matching_student.id
    else:
        new_student = Student(
            name=account.name,
            roll_number=account.roll_number,
            class_name=account.class_name,
            section=account.section,
            contact=account.contact
        )
        db.session.add(new_student)
        db.session.flush()
        account.student_id = new_student.id

    db.session.commit()
    flash('Student account approved.', 'success')
    return redirect(url_for('teacher.approvals'))


@teacher_bp.route('/teacher/approvals/reject/<int:account_id>', methods=['POST'])
@login_required
@teacher_required
def reject_account(account_id):
    account = StudentAccount.query.get_or_404(account_id)
    db.session.delete(account)
    db.session.commit()
    flash('Student account rejected.', 'danger')
    return redirect(url_for('teacher.approvals'))
