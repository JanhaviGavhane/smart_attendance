from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import select
from database import db
from models import Student

student_bp = Blueprint("students", __name__, url_prefix="/students")


@student_bp.route("/", methods=["GET", "POST"])
@login_required
def manage_students():
    if request.method == "POST":
        roll_number = request.form.get("roll_number", "").strip()
        name = request.form.get("name", "").strip()
        division = request.form.get("division", "").strip()

        if not roll_number or not name or not division:
            flash("Please fill in all student fields.", "error")
            return redirect(url_for("students.manage_students"))

        if len(roll_number) > 30 or len(name) > 100 or len(division) > 50:
            flash("One or more fields exceed the allowed length.", "error")
            return redirect(url_for("students.manage_students"))

        existing_student = db.session.execute(
            select(Student).where(
                Student.teacher_id == current_user.id,
                Student.roll_number == roll_number
            )
        ).scalar_one_or_none()

        if existing_student:
            flash("This roll number already exists in your student list.", "error")
            return redirect(url_for("students.manage_students"))

        student = Student(
            teacher_id=current_user.id,
            roll_number=roll_number,
            name=name,
            division=division
        )

        db.session.add(student)
        db.session.commit()

        flash("Student added successfully.", "success")
        return redirect(url_for("students.manage_students"))

    students = db.session.execute(
        select(Student)
        .where(Student.teacher_id == current_user.id)
        .order_by(Student.roll_number)
    ).scalars().all()

    return render_template("students.html", students=students)


@student_bp.route("/<int:student_id>/delete", methods=["POST"])
@login_required
def delete_student(student_id):
    student = db.session.execute(
        select(Student).where(
            Student.id == student_id,
            Student.teacher_id == current_user.id
        )
    ).scalar_one_or_none()

    if student is None:
        flash("Student not found.", "error")
        return redirect(url_for("students.manage_students"))

    if student.attendance_records:
        flash(
            "This student has attendance records and cannot be deleted. "
            "Keeping the records preserves report accuracy.",
            "error"
        )
        return redirect(url_for("students.manage_students"))

    db.session.delete(student)
    db.session.commit()

    flash("Student deleted successfully.", "success")
    return redirect(url_for("students.manage_students"))