from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import select
from database import db
from models import SyllabusTopic

syllabus_bp = Blueprint("syllabus", __name__, url_prefix="/syllabus")


@syllabus_bp.route("/", methods=["GET", "POST"])
@login_required
def syllabus_home():
    if request.method == "POST":
        subject_name = request.form.get("subject_name", "").strip()
        topic_name = request.form.get("topic_name", "").strip()

        if not subject_name or not topic_name:
            flash("Enter both subject and topic.", "error")
            return redirect(url_for("syllabus.syllabus_home"))

        if len(subject_name) > 100 or len(topic_name) > 200:
            flash("Subject or topic name is too long.", "error")
            return redirect(url_for("syllabus.syllabus_home"))

        topic = SyllabusTopic(
            teacher_id=current_user.id,
            subject_name=subject_name,
            topic_name=topic_name,
            is_completed=False
        )

        db.session.add(topic)
        db.session.commit()

        flash("Syllabus topic added.", "success")
        return redirect(url_for("syllabus.syllabus_home"))

    topics = db.session.execute(
        select(SyllabusTopic)
        .where(SyllabusTopic.teacher_id == current_user.id)
        .order_by(SyllabusTopic.subject_name, SyllabusTopic.id)
    ).scalars().all()

    return render_template("syllabus.html", topics=topics)


@syllabus_bp.route("/<int:topic_id>/toggle", methods=["POST"])
@login_required
def toggle_topic(topic_id):
    topic = db.session.execute(
        select(SyllabusTopic).where(
            SyllabusTopic.id == topic_id,
            SyllabusTopic.teacher_id == current_user.id
        )
    ).scalar_one_or_none()

    if topic is None:
        flash("Topic not found.", "error")
        return redirect(url_for("syllabus.syllabus_home"))

    topic.is_completed = not topic.is_completed
    db.session.commit()

    flash("Syllabus progress updated.", "success")
    return redirect(url_for("syllabus.syllabus_home"))