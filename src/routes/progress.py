# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify, session
from src.models.user import db, User
from src.models.course import Course, Lecture
from src.models.progress import StudentProgress
from datetime import datetime

progress_bp = Blueprint("progress_routes", __name__)

# --- Student Progress Tracking ---
@progress_bp.route("/progress/lecture/<int:lecture_id>/complete", methods=["POST"])
def mark_lecture_complete(lecture_id):
    if "user_id" not in session:
        return jsonify({"error": "يجب تسجيل الدخول لتحديث حالة التقدم."}), 401

    user_id = session["user_id"]
    lecture = Lecture.query.get(lecture_id)

    if not lecture:
        return jsonify({"error": "المحاضرة غير موجودة."}), 404

    # Check if progress record already exists
    existing_progress = StudentProgress.query.filter_by(user_id=user_id, lecture_id=lecture_id).first()
    if existing_progress:
        # Optionally, update the completed_date if re-completing, or just confirm it's done
        existing_progress.completed_date = datetime.utcnow()
        db.session.add(existing_progress)
        message = "تم تحديث تاريخ إكمال المحاضرة."
    else:
        new_progress = StudentProgress(user_id=user_id, lecture_id=lecture_id)
        db.session.add(new_progress)
        message = "تم تسجيل إكمال المحاضرة بنجاح."
    
    try:
        db.session.commit()
        return jsonify({"message": message}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"حدث خطأ أثناء تحديث التقدم: {str(e)}"}), 500

@progress_bp.route("/progress/course/<int:course_id>", methods=["GET"])
def get_course_progress(course_id):
    if "user_id" not in session:
        return jsonify({"error": "يجب تسجيل الدخول لعرض حالة التقدم."}), 401
    
    user_id = session["user_id"]
    
    # Get all lectures for the course
    lectures_in_course = Lecture.query.filter_by(course_id=course_id).all()
    if not lectures_in_course:
        return jsonify({"message": "لا توجد محاضرات في هذا المقرر بعد."}), 200 # Or 404 if course itself not found

    completed_lectures_ids = [
        p.lecture_id for p in StudentProgress.query.filter_by(user_id=user_id)
        .join(Lecture).filter(Lecture.course_id == course_id).all()
    ]

    total_lectures = len(lectures_in_course)
    completed_count = len(completed_lectures_ids)
    
    progress_percentage = (completed_count / total_lectures) * 100 if total_lectures > 0 else 0

    return jsonify({
        "course_id": course_id,
        "total_lectures": total_lectures,
        "completed_lectures": completed_count,
        "progress_percentage": round(progress_percentage, 2),
        "completed_lecture_ids": completed_lectures_ids
    }), 200

@progress_bp.route("/progress/my_summary", methods=["GET"])
def get_my_overall_progress_summary():
    if "user_id" not in session:
        return jsonify({"error": "يجب تسجيل الدخول لعرض ملخص التقدم."}), 401
    user_id = session["user_id"]

    # This is a simplified summary. A more complex one might involve courses enrolled in.
    # For now, let's count all completed lectures by the user.
    completed_lectures = StudentProgress.query.filter_by(user_id=user_id).count()
    
    # Potentially, list courses the user has made progress in
    courses_with_progress = db.session.query(StudentProgress.lecture_id, Lecture.course_id).distinct()\
        .join(Lecture, StudentProgress.lecture_id == Lecture.id)\
        .filter(StudentProgress.user_id == user_id).all()
    
    distinct_course_ids = list(set([cp.course_id for cp in courses_with_progress]))

    return jsonify({
        "user_id": user_id,
        "total_completed_lectures_overall": completed_lectures,
        "courses_with_progress_ids": distinct_course_ids 
        # Add more detailed per-course progress if needed here or by calling /progress/course/<id>
    }), 200


