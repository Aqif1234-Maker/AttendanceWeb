from datetime import date, datetime
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from .. import db
from ..models import Student, Attendance, StudentAccount
from . import teacher_required


api_bp = Blueprint('api', __name__, url_prefix='/api')


def _parse_filters():
    name = request.args.get('name', '').strip()
    class_name = request.args.get('class', '').strip()
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    def _parse_date(value):
        if not value:
            return None
        try:
            return datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError:
            return None

    return name, class_name, _parse_date(date_from), _parse_date(date_to)


@api_bp.route('/students')
@login_required
@teacher_required
def api_students():
    class_name = request.args.get('class')
    section = request.args.get('section')

    query = Student.query
    if class_name:
        query = query.filter_by(class_name=class_name)
    if section:
        query = query.filter_by(section=section)

    students = query.order_by(Student.name.asc()).all()

    if not students and class_name and section:
        accounts = StudentAccount.query.filter_by(
            approved=True,
            class_name=class_name,
            section=section
        ).all()
        if accounts:
            for account in accounts:
                existing = Student.query.filter_by(
                    roll_number=account.roll_number,
                    class_name=account.class_name,
                    section=account.section
                ).first()
                if not existing:
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
            students = query.order_by(Student.name.asc()).all()
    return jsonify([
        {
            'id': s.id,
            'name': s.name,
            'roll_number': s.roll_number,
            'class': s.class_name,
            'section': s.section
        }
        for s in students
    ])


@api_bp.route('/section-stats')
@login_required
@teacher_required
def api_section_stats():
    class_name = request.args.get('class')
    section = request.args.get('section')
    today = date.today()

    query = Student.query
    if class_name:
        query = query.filter_by(class_name=class_name)
    if section:
        query = query.filter_by(section=section)

    student_ids = [s.id for s in query.all()]
    total = len(student_ids)

    if total == 0:
        return jsonify({'total': 0, 'present': 0, 'absent': 0, 'late': 0, 'percent': 0})

    attendance_query = Attendance.query.filter(Attendance.date == today, Attendance.student_id.in_(student_ids))
    present = attendance_query.filter_by(status='Present').count()
    absent = attendance_query.filter_by(status='Absent').count()
    late = attendance_query.filter_by(status='Late').count()
    percent = round((present / total) * 100, 2) if total else 0

    return jsonify({'total': total, 'present': present, 'absent': absent, 'late': late, 'percent': percent})


@api_bp.route('/chart-data')
@login_required
@teacher_required
def api_chart_data():
    today = date.today()
    present = Attendance.query.filter_by(date=today, status='Present').count()
    absent = Attendance.query.filter_by(date=today, status='Absent').count()
    late = Attendance.query.filter_by(date=today, status='Late').count()
    return jsonify({'present': present, 'absent': absent, 'late': late})


@api_bp.route('/recent-attendance')
@login_required
@teacher_required
def api_recent_attendance():
    class_name = request.args.get('class')
    section = request.args.get('section')

    query = db.session.query(Attendance, Student).join(Student)

    if class_name:
        query = query.filter(Student.class_name == class_name)
    if section:
        query = query.filter(Student.section == section)

    records = (
        query.order_by(Attendance.date.desc(), Attendance.id.desc())
        .limit(10)
        .all()
    )

    return jsonify([
        {
            'name': student.name,
            'class': student.class_name,
            'section': student.section,
            'date': att.date.strftime('%Y-%m-%d'),
            'status': att.status
        }
        for att, student in records
    ])


@api_bp.route('/attendance', methods=['POST'])
@login_required
@teacher_required
def api_attendance_submit():
    payload = request.get_json(silent=True) or {}
    date_str = payload.get('date')
    records = payload.get('records', {})

    if not date_str:
        return jsonify({'error': 'Date is required'}), 400

    try:
        attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

    saved = 0
    for student_id, status in records.items():
        try:
            student_id = int(student_id)
        except (TypeError, ValueError):
            continue
        if status not in ('Present', 'Absent', 'Late'):
            continue
        existing = Attendance.query.filter_by(student_id=student_id, date=attendance_date).first()
        if existing:
            existing.status = status
            existing.marked_by = current_user.id
        else:
            db.session.add(Attendance(
                student_id=student_id,
                date=attendance_date,
                status=status,
                marked_by=current_user.id
            ))
        saved += 1

    db.session.commit()
    return jsonify({'saved': saved})


@api_bp.route('/report-data')
@login_required
@teacher_required
def api_report_data():
    name, class_name, date_from, date_to = _parse_filters()

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

    return jsonify([
        {
            'name': student.name,
            'roll_number': student.roll_number,
            'class': student.class_name,
            'section': student.section,
            'date': att.date.strftime('%Y-%m-%d'),
            'status': att.status
        }
        for att, student in records
    ])


@api_bp.route('/report-chart')
@login_required
@teacher_required
def api_report_chart():
    name, class_name, date_from, date_to = _parse_filters()

    query = db.session.query(Attendance, Student).join(Student)

    if name:
        query = query.filter(Student.name.ilike(f'%{name}%'))
    if class_name:
        query = query.filter(Student.class_name == class_name)
    if date_from:
        query = query.filter(Attendance.date >= date_from)
    if date_to:
        query = query.filter(Attendance.date <= date_to)

    present = query.filter(Attendance.status == 'Present').count()
    absent = query.filter(Attendance.status == 'Absent').count()
    late = query.filter(Attendance.status == 'Late').count()

    return jsonify({'present': present, 'absent': absent, 'late': late})
