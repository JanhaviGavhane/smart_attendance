from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint
from database import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    students = db.relationship(
        "Student",
        backref="teacher",
        cascade="all, delete-orphan"
    )

    subjects = db.relationship(
        "Subject",
        backref="teacher",
        cascade="all, delete-orphan"
    )

    syllabus_topics = db.relationship(
        "SyllabusTopic",
        backref="teacher",
        cascade="all, delete-orphan"
    )


class Student(db.Model):
    __tablename__ = "students"
    __table_args__ = (
        UniqueConstraint("teacher_id", "roll_number", name="uq_student_teacher_roll"),
    )

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    roll_number = db.Column(db.String(30), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    division = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Subject(db.Model):
    __tablename__ = "subjects"
    __table_args__ = (
        UniqueConstraint("teacher_id", "name", name="uq_subject_teacher_name"),
    )

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class AttendanceSession(db.Model):
    __tablename__ = "attendance_sessions"

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    subject_id = db.Column(
        db.Integer,
        db.ForeignKey("subjects.id"),
        nullable=False
    )
    division = db.Column(db.String(50), nullable=False)
    session_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    subject = db.relationship("Subject", backref="attendance_sessions")

    records = db.relationship(
        "AttendanceRecord",
        backref="session",
        cascade="all, delete-orphan"
    )


class AttendanceRecord(db.Model):
    __tablename__ = "attendance_records"
    __table_args__ = (
        UniqueConstraint("session_id", "student_id", name="uq_session_student"),
    )

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(
        db.Integer,
        db.ForeignKey("attendance_sessions.id"),
        nullable=False,
        index=True
    )
    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id"),
        nullable=False,
        index=True
    )
    status = db.Column(db.String(20), nullable=False, default="present")
    marked_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    marked_by = db.Column(db.String(20), nullable=False, default="manual")

    student = db.relationship("Student", backref="attendance_records")


class SyllabusTopic(db.Model):
    __tablename__ = "syllabus_topics"

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    subject_name = db.Column(db.String(100), nullable=False)
    topic_name = db.Column(db.String(200), nullable=False)
    is_completed = db.Column(db.Boolean, nullable=False, default=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )