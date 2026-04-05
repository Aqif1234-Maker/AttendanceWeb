from .. import db


class Attendance(db.Model):
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('Present', 'Absent', 'Late'), nullable=False)
    marked_by = db.Column(db.Integer, db.ForeignKey('teachers.id'))

    __table_args__ = (
        db.UniqueConstraint('student_id', 'date', name='unique_attendance'),
    )
