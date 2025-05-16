# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify, session
from src.models.user import db, User, Course, ForumTopic, ForumPost, Announcement
from datetime import datetime

forum_announcement_bp = Blueprint("forum_announcement_routes", __name__)

# --- Forum Topic Management (Admin & Authenticated Users) ---
@forum_announcement_bp.route("/forums/topics", methods=["POST"])
def create_forum_topic():
    if "user_id" not in session:
        return jsonify({"error": "يجب تسجيل الدخول لإنشاء موضوع جديد."}), 401
    
    data = request.get_json()
    title = data.get("title")
    course_id = data.get("course_id") # Optional, to associate topic with a course
    user_id = session["user_id"]

    if not title:
        return jsonify({"error": "عنوان الموضوع مطلوب."}), 400

    new_topic = ForumTopic(title=title, created_by_user_id=user_id, course_id=course_id)
    db.session.add(new_topic)
    try:
        db.session.commit()
        return jsonify({"message": "تم إنشاء الموضوع بنجاح.", "topic_id": new_topic.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"حدث خطأ أثناء إنشاء الموضوع: {str(e)}"}), 500

@forum_announcement_bp.route("/forums/topics", methods=["GET"])
def list_forum_topics():
    # Add pagination later if needed
    course_id_filter = request.args.get("course_id")
    query = ForumTopic.query.order_by(ForumTopic.last_post_date.desc())
    if course_id_filter:
        query = query.filter_by(course_id=course_id_filter)
    
    topics = query.all()
    output = []
    for topic in topics:
        output.append({
            "id": topic.id,
            "title": topic.title,
            "creator": topic.creator.username if topic.creator else "N/A",
            "course_id": topic.course_id,
            "creation_date": topic.creation_date.strftime("%Y-%m-%d %H:%M:%S"),
            "last_post_date": topic.last_post_date.strftime("%Y-%m-%d %H:%M:%S"),
            "post_count": len(topic.posts) # Basic post count
        })
    return jsonify({"topics": output}), 200

@forum_announcement_bp.route("/forums/topics/<int:topic_id>", methods=["GET"])
def get_forum_topic_details(topic_id):
    topic = ForumTopic.query.get_or_404(topic_id)
    posts_output = []
    # Simple ordering, can be made more complex (e.g., threaded view)
    for post in sorted(topic.posts, key=lambda p: p.creation_date):
        posts_output.append({
            "id": post.id,
            "author": post.author.username if post.author else "N/A",
            "content": post.content,
            "creation_date": post.creation_date.strftime("%Y-%m-%d %H:%M:%S"),
            "parent_post_id": post.parent_post_id
        })
    return jsonify({
        "id": topic.id,
        "title": topic.title,
        "creator": topic.creator.username if topic.creator else "N/A",
        "creation_date": topic.creation_date.strftime("%Y-%m-%d %H:%M:%S"),
        "posts": posts_output
    }), 200

# --- Forum Post Management (Authenticated Users) ---
@forum_announcement_bp.route("/forums/topics/<int:topic_id>/posts", methods=["POST"])
def create_forum_post(topic_id):
    if "user_id" not in session:
        return jsonify({"error": "يجب تسجيل الدخول لإضافة رد."}), 401

    topic = ForumTopic.query.get_or_404(topic_id)
    data = request.get_json()
    content = data.get("content")
    parent_post_id = data.get("parent_post_id") # For replies
    user_id = session["user_id"]

    if not content:
        return jsonify({"error": "محتوى الرد مطلوب."}), 400

    new_post = ForumPost(
        topic_id=topic.id, 
        user_id=user_id, 
        content=content, 
        parent_post_id=parent_post_id
    )
    db.session.add(new_post)
    topic.last_post_date = datetime.utcnow() # Update topic's last post date
    try:
        db.session.commit()
        return jsonify({"message": "تمت إضافة الرد بنجاح.", "post_id": new_post.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"حدث خطأ أثناء إضافة الرد: {str(e)}"}), 500

# --- Announcement Management (Admin) ---
@forum_announcement_bp.route("/admin/announcements", methods=["POST"])
def create_announcement():
    if not session.get("is_admin"):
        return jsonify({"error": "غير مصرح لك بإنشاء إعلان."}), 403
    
    data = request.get_json()
    title = data.get("title")
    content = data.get("content")
    course_id = data.get("course_id") # Optional
    is_published = data.get("is_published", True)
    admin_user_id = session["user_id"]

    if not title or not content:
        return jsonify({"error": "عنوان الإعلان ومحتواه مطلوبان."}), 400

    new_announcement = Announcement(
        title=title, 
        content=content, 
        created_by_user_id=admin_user_id, 
        course_id=course_id, 
        is_published=is_published
    )
    db.session.add(new_announcement)
    try:
        db.session.commit()
        return jsonify({"message": "تم إنشاء الإعلان بنجاح.", "announcement_id": new_announcement.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"حدث خطأ أثناء إنشاء الإعلان: {str(e)}"}), 500

@forum_announcement_bp.route("/admin/announcements/<int:ann_id>", methods=["PUT"])
def update_announcement(ann_id):
    if not session.get("is_admin"):
        return jsonify({"error": "غير مصرح لك بتعديل الإعلان."}), 403

    announcement = Announcement.query.get_or_404(ann_id)
    data = request.get_json()
    announcement.title = data.get("title", announcement.title)
    announcement.content = data.get("content", announcement.content)
    announcement.course_id = data.get("course_id", announcement.course_id)
    announcement.is_published = data.get("is_published", announcement.is_published)
    try:
        db.session.commit()
        return jsonify({"message": "تم تحديث الإعلان بنجاح."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"حدث خطأ أثناء تحديث الإعلان: {str(e)}"}), 500

@forum_announcement_bp.route("/admin/announcements/<int:ann_id>", methods=["DELETE"])
def delete_announcement(ann_id):
    if not session.get("is_admin"):
        return jsonify({"error": "غير مصرح لك بحذف الإعلان."}), 403

    announcement = Announcement.query.get_or_404(ann_id)
    db.session.delete(announcement)
    try:
        db.session.commit()
        return jsonify({"message": "تم حذف الإعلان بنجاح."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"حدث خطأ أثناء حذف الإعلان: {str(e)}"}), 500

# --- Public Route to View Announcements ---
@forum_announcement_bp.route("/announcements", methods=["GET"])
def list_announcements():
    course_id_filter = request.args.get("course_id")
    query = Announcement.query.filter_by(is_published=True).order_by(Announcement.creation_date.desc())
    if course_id_filter:
        query = query.filter_by(course_id=course_id_filter)
        
    announcements = query.all()
    output = []
    for ann in announcements:
        output.append({
            "id": ann.id,
            "title": ann.title,
            "content": ann.content,
            "creator": ann.creator.username if ann.creator else "N/A",
            "course_id": ann.course_id,
            "creation_date": ann.creation_date.strftime("%Y-%m-%d %H:%M:%S")
        })
    return jsonify({"announcements": output}), 200


