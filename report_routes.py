from collections import defaultdict
from datetime import date

from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import select

from database import db
from models import AttendanceSession, AttendanceRecord, Subject


report_bp = Blueprint("reports", __name__, url_prefix="/reports")


@report_bp.route("/")
@login_required
def reports_home():
    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()
    subject_id = request.args.get("subject_id", "").strip()
    division = request.args.get("division", "").strip()
    lecture_id = request.args.get("lecture_id", "").strip()
    method = request.args.get("method", "all").strip().lower()

    if method not in ("all", "voice", "manual"):
        method = "all"

    # Get only this teacher's subjects.
    subjects = db.session.execute(
        select(Subject)
        .where(Subject.teacher_id == current_user.id)
        .order_by(Subject.name)
    ).scalars().all()

    # Get all saved sessions belonging to this teacher.
    all_sessions = db.session.execute(
        select(AttendanceSession)
        .where(AttendanceSession.teacher_id == current_user.id)
        .order_by(
            AttendanceSession.session_date.desc(),
            AttendanceSession.id.desc()
        )
    ).scalars().all()

    # Validate date filters.
    parsed_start = None
    parsed_end = None

    if start_date:
        try:
            parsed_start = date.fromisoformat(start_date)
        except ValueError:
            start_date = ""

    if end_date:
        try:
            parsed_end = date.fromisoformat(end_date)
        except ValueError:
            end_date = ""

    # Apply filters to the saved sessions.
    filtered_sessions = []

    for item in all_sessions:
        if parsed_start and item.session_date < parsed_start:
            continue

        if parsed_end and item.session_date > parsed_end:
            continue

        if subject_id:
            if not subject_id.isdigit():
                continue
            if item.subject_id != int(subject_id):
                continue

        if division and item.division != division:
            continue

        if lecture_id:
            if not lecture_id.isdigit():
                continue
            if item.id != int(lecture_id):
                continue

        filtered_sessions.append(item)

    # Build lecture summaries, chart data and student attendance totals.
    session_rows = []
    chart_labels = []
    chart_present = []
    chart_absent = []
    student_stats = defaultdict(
        lambda: {
            "name": "",
            "roll_number": "",
            "subject": "",
            "division": "",
            "present": 0,
            "total": 0
        }
    )

    attendance_details = []

    for item in filtered_sessions:
        records = item.records

        # Apply the marking-method filter to the attendance records.
        if method != "all":
            records = [
                record for record in records
                if (record.marked_by or "").lower() == method
            ]

        present_count = sum(
            1 for record in records
            if (record.status or "").lower() == "present"
        )

        absent_count = sum(
            1 for record in records
            if (record.status or "").lower() == "absent"
        )

        label = (
            f"{item.session_date.isoformat()} | "
            f"{item.subject.name} | "
            f"{item.division} | Session #{item.id}"
        )

        chart_labels.append(label)
        chart_present.append(present_count)
        chart_absent.append(absent_count)

        session_rows.append({
            "id": item.id,
            "date": item.session_date.isoformat(),
            "subject": item.subject.name,
            "division": item.division,
            "present": present_count,
            "absent": absent_count,
            "total": len(records)
        })

        for record in records:
            student = record.student

            # Do not include another teacher's student in this report.
            if student.teacher_id != current_user.id:
                continue

            key = (
                record.student_id,
                item.subject_id,
                item.division
            )

            stats = student_stats[key]
            stats["name"] = student.name
            stats["roll_number"] = student.roll_number
            stats["subject"] = item.subject.name
            stats["division"] = item.division
            stats["total"] += 1

            if (record.status or "").lower() == "present":
                stats["present"] += 1

            attendance_details.append({
                "date": item.session_date.isoformat(),
                "session_id": item.id,
                "subject": item.subject.name,
                "division": item.division,
                "roll_number": student.roll_number,
                "name": student.name,
                "status": record.status.title(),
                "marked_by": (record.marked_by or "manual").title()
            })

    # Calculate attendance percentages and identify students below 75%.
    reports = []

    for stats in student_stats.values():
        stats["percentage"] = round(
            stats["present"] / stats["total"] * 100, 2
        ) if stats["total"] else 0

        if stats["percentage"] < 75:
            reports.append(stats)

    reports.sort(key=lambda row: row["percentage"])

    # Show divisions that exist in this teacher's saved sessions.
    divisions = sorted({
        item.division
        for item in all_sessions
        if item.division
    })

    return render_template(
        "reports.html",
        reports=reports,
        subjects=subjects,
        sessions=all_sessions,
        start_date=start_date,
        end_date=end_date,
        subject_id=subject_id,
        division=division,
        divisions=divisions,
        lecture_id=lecture_id,
        method=method,
        session_rows=session_rows,
        chart_labels=chart_labels,
        chart_present=chart_present,
        chart_absent=chart_absent,
        attendance_details=attendance_details
    )
