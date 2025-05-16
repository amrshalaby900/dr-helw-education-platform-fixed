# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify, session
from src.models.user import db, User
from src.models.course import Course, Lecture
from datetime import datetime

course_bp = Blueprint("course_routes", __name__)

# --- Course Management (Admin) ---
@course_bp.route("/admin/courses", methods=["POST"])
def create_course():
    if not session.get("is_admin"):
        return jsonify({"error": "غير مصرح لك بإنشاء مقرر دراسي."}), 403
    
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")

    if not title:
        return jsonify({"error": "عنوان المقرر الدراسي مطلوب."}), 400

    admin_user_id = session.get("user_id") # Get admin user ID from session
    new_course = Course(title=title, description=description, created_by_user_id=admin_user_id)
    db.session.add(new_course)
    try:
        db.session.commit()
        return jsonify({"message": "تم إنشاء المقرر الدراسي بنجاح.", "course_id": new_course.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"حدث خطأ أثناء إنشاء المقرر: {str(e)}"}), 500

@course_bp.route("/admin/courses/<int:course_id>", methods=["PUT"])
def update_course(course_id):
    if not session.get("is_admin"):
        return jsonify({"error": "غير مصرح لك بتعديل المقرر الدراسي."}), 403

    course = Course.query.get_or_404(course_id)
    data = request.get_json()
    course.title = data.get("title", course.title)
    course.description = data.get("description", course.description)
    try:
        db.session.commit()
        return jsonify({"message": "تم تحديث المقرر الدراسي بنجاح."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"حدث خطأ أثناء تحديث المقرر: {str(e)}"}), 500

@course_bp.route("/admin/courses/<int:course_id>", methods=["DELETE"])
def delete_course(course_id):
    if not session.get("is_admin"):
        return jsonify({"error": "غير مصرح لك بحذف المقرر الدراسي."}), 403

    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    try:
        db.session.commit()
        return jsonify({"message": "تم حذف المقرر الدراسي بنجاح."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"حدث خطأ أثناء حذف المقرر: {str(e)}"}), 500

# --- Lecture Management (Admin) ---
@course_bp.route("/admin/courses/<int:course_id>/lectures", methods=["POST"])
def create_lecture(course_id):
    if not session.get("is_admin"):
        return jsonify({"error": "غير مصرح لك بإنشاء محاضرة."}), 403

    course = Course.query.get_or_404(course_id)
    data = request.get_json()
    title = data.get("title")
    video_url = data.get("video_url")
    text_content = data.get("text_content")
    order = data.get("order", 0)

    if not title:
        return jsonify({"error": "عنوان المحاضرة مطلوب."}), 400

    new_lecture = Lecture(
        course_id=course.id, 
        title=title, 
        video_url=video_url, 
        text_content=text_content, 
        order=order
    )
    db.session.add(new_lecture)
    try:
        db.session.commit()
        return jsonify({"message": "تم إنشاء المحاضرة بنجاح.", "lecture_id": new_lecture.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"حدث خطأ أثناء إنشاء المحاضرة: {str(e)}"}), 500

@course_bp.route("/admin/lectures/<int:lecture_id>", methods=["PUT"])
def update_lecture(lecture_id):
    if not session.get("is_admin"):
        return jsonify({"error": "غير مصرح لك بتعديل المحاضرة."}), 403

    lecture = Lecture.query.get_or_404(lecture_id)
    data = request.get_json()
    lecture.title = data.get("title", lecture.title)
    lecture.video_url = data.get("video_url", lecture.video_url)
    lecture.text_content = data.get("text_content", lecture.text_content)
    lecture.order = data.get("order", lecture.order)
    try:
        db.session.commit()
        return jsonify({"message": "تم تحديث المحاضرة بنجاح."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"حدث خطأ أثناء تحديث المحاضرة: {str(e)}"}), 500

@course_bp.route("/admin/lectures/<int:lecture_id>", methods=["DELETE"])
def delete_lecture(lecture_id):
    if not session.get("is_admin"):
        return jsonify({"error": "غير مصرح لك بحذف المحاضرة."}), 403

    lecture = Lecture.query.get_or_404(lecture_id)
    db.session.delete(lecture)
    try:
        db.session.commit()
        return jsonify({"message": "تم حذف المحاضرة بنجاح."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"حدث خطأ أثناء حذف المحاضرة: {str(e)}"}), 500

# --- Public Routes to View Courses and Lectures ---
@course_bp.route("/courses", methods=["GET"])
def list_courses():
    courses = Course.query.order_by(Course.creation_date.desc()).all()
    output = []
    for course in courses:
        output.append({
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "creator": course.creator.username if course.creator else "N/A", # Assuming creator relationship is set up
            "creation_date": course.creation_date.strftime("%Y-%m-%d %H:%M:%S")
        })
    return jsonify({"courses": output}), 200

@course_bp.route("/courses/<int:course_id>", methods=["GET"])
def get_course_details(course_id):
    course = Course.query.get_or_404(course_id)
    lectures_output = []
    for lecture in sorted(course.lectures, key=lambda l: l.order):
        lectures_output.append({
            "id": lecture.id,
            "title": lecture.title,
            "video_url": lecture.video_url,
            "text_content": lecture.text_content,
            "order": lecture.order
        })
    return jsonify({
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "creator": course.creator.username if course.creator else "N/A",
        "creation_date": course.creation_date.strftime("%Y-%m-%d %H:%M:%S"),
        "lectures": lectures_output
    }), 200

@course_bp.route("/lectures/<int:lecture_id>", methods=["GET"])
def get_lecture_details(lecture_id):
    # This route might be redundant if lecture details are always fetched within a course context
    # but can be useful for direct access or specific lecture features like comments/progress marking
    lecture = Lecture.query.get_or_404(lecture_id)
    return jsonify({
        "id": lecture.id,
        "title": lecture.title,
        "video_url": lecture.video_url,
        "text_content": lecture.text_content,
        "order": lecture.order,
        "course_id": lecture.course_id,
        "course_title": lecture.course.title # Assuming course relationship is set up
    }), 200


