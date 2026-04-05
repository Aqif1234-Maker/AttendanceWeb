from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .. import db


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    roll_number = db.Column(db.String(50), unique=True, nullable=False)
    class_name = db.Column('class', db.String(20), nullable=False)
    section = db.Column(db.String(10), nullable=False)
    contact = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    attendance = db.relationship('Attendance', backref='student', lazy=True, cascade='all, delete-orphan')


class StudentAccount(UserMixin, db.Model):
    __tablename__ = 'student_accounts'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    roll_number = db.Column(db.String(50), unique=True, nullable=False)
    class_name = db.Column('class', db.String(20), nullable=False)
    section = db.Column(db.String(10), nullable=False)
    contact = db.Column(db.String(20))
    password = db.Column(db.String(255), nullable=False)
    approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    student = db.relationship('Student', backref='account', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
