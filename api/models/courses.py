from datetime import datetime
from ..utils import db


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=True)
    courses = db.relationship('StudentCourse', backref='student', lazy=True)

    def __repr__(self):
        return f'<Student {self.name}>'


class Course(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    teacher = db.Column(db.String(50), nullable=False)
    students = db.relationship('StudentCourse', backref='course', lazy=True)

    def __repr__(self):
        return f'<Course {self.name}>'


class StudentCourse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.String, db.ForeignKey('course.id'), nullable=False)
    grade = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('student_id', 'course_id', name='_student_course_uc'),)

    def __repr__(self):
        return f'<StudentCourse student_id={self.student_id} course_id={self.course_id} grade={self.grade}>'







