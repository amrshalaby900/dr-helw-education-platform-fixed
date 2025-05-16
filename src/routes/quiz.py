# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify, session
from src.models.user import db, User, Course, Lecture, Quiz, Question, StudentAnswer
from datetime import datetime

quiz_bp = Blueprint("quiz_routes", __name__)

# --- Quiz Management (Admin) ---
@quiz_bp.route("/admin/quizzes", methods=["POST"])
def create_quiz():
    if not session.get("is_admin"):
        return jsonify({"error": "غير مصرح لك بإنشاء اختبار."}), 403
    
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    course_id = data.get("course_id")
    lecture_id = data.get("lecture_id") # Optional

    if not title or not course_id:
        return jsonify({"error": "عنوان الاختبار ومعرف المقرر مطلوبان."}), 400

    new_quiz = Quiz(title=title, description=description, course_id=course_id, lecture_id=lecture_id)
    db.session.add(new_quiz)
    try:
        db.session.commit()
        return jsonify({"message": "تم إنشاء الاختبار بنجاح.", "quiz_id": new_quiz.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"حدث خطأ أثناء إنشاء الاختبار: {str(e)}"}), 500

@quiz_bp.route("/admin/quizzes/<int:quiz_id>", methods=["PUT"])
def update_quiz(quiz_id):
    if not session.get("is_admin"):
        return jsonify({"error": "غير مصرح لك بتعديل الاختبار."}), 403

    quiz = Quiz.query.get_or_404(quiz_id)
    data = request.get_json()
    quiz.title = data.get("title", quiz.title)
    quiz.description = data.get("description", quiz.description)
    quiz.course_id = data.get("course_id", quiz.course_id)
    quiz.lecture_id = data.get("lecture_id", quiz.lecture_id)
    try:
        db.session.commit()
        return jsonify({"message": "تم تحديث الاختبار بنجاح."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"حدث خطأ أثناء تحديث الاختبار: {str(e)}"}), 500

@quiz_bp.route("/admin/quizzes/<int:quiz_id>", methods=["DELETE"])
def delete_quiz(quiz_id):
    if not session.get("is_admin"):
        return jsonify({"error": "غير مصرح لك بحذف الاختبار."}), 403

    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    try:
        db.session.commit()
        return jsonify({"message": "تم حذف الاختبار بنجاح."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"حدث خطأ أثناء حذف الاختبار: {str(e)}"}), 500

# --- Question Management (Admin) ---
@quiz_bp.route("/admin/quizzes/<int:quiz_id>/questions", methods=["POST"])
def add_question_to_quiz(quiz_id):
    if not session.get("is_admin"):
        return jsonify({"error": "غير مصرح لك بإضافة سؤال."}), 403

    quiz = Quiz.query.get_or_404(quiz_id)
    data = request.get_json()
    text = data.get("text")
    question_type = data.get("question_type", "multiple_choice")
    options = data.get("options") # JSON for multiple choice
    correct_answer = data.get("correct_answer")

    if not text:
        return jsonify({"error": "نص السؤال مطلوب."}), 400

    new_question = Question(
        quiz_id=quiz.id, 
        text=text, 
        question_type=question_type, 
        options=options, 
        correct_answer=correct_answer
    )
    db.session.add(new_question)
    try:
        db.session.commit()
        return jsonify({"message": "تمت إضافة السؤال بنجاح.", "question_id": new_question.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"حدث خطأ أثناء إضافة السؤال: {str(e)}"}), 500

@quiz_bp.route("/admin/questions/<int:question_id>", methods=["PUT"])
def update_question(question_id):
    if not session.get("is_admin"):
        return jsonify({"error": "غير مصرح لك بتعديل السؤال."}), 403

    question = Question.query.get_or_404(question_id)
    data = request.get_json()
    question.text = data.get("text", question.text)
    question.question_type = data.get("question_type", question.question_type)
    question.options = data.get("options", question.options)
    question.correct_answer = data.get("correct_answer", question.correct_answer)
    try:
        db.session.commit()
        return jsonify({"message": "تم تحديث السؤال بنجاح."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"حدث خطأ أثناء تحديث السؤال: {str(e)}"}), 500

@quiz_bp.route("/admin/questions/<int:question_id>", methods=["DELETE"])
def delete_question(question_id):
    if not session.get("is_admin"):
        return jsonify({"error": "غير مصرح لك بحذف السؤال."}), 403

    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    try:
        db.session.commit()
        return jsonify({"message": "تم حذف السؤال بنجاح."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"حدث خطأ أثناء حذف السؤال: {str(e)}"}), 500

# --- Quiz Taking (Student) ---
@quiz_bp.route("/quizzes/<int:quiz_id>", methods=["GET"])
def get_quiz_for_student(quiz_id):
    # Ensure user is logged in (add more specific access control if needed, e.g., enrolled in course)
    if "user_id" not in session:
        return jsonify({"error": "يرجى تسجيل الدخول لعرض الاختبار."}), 401
        
    quiz = Quiz.query.get_or_404(quiz_id)
    questions_output = []
    for q in quiz.questions:
        questions_output.append({
            "id": q.id,
            "text": q.text,
            "question_type": q.question_type,
            "options": q.options # Send options for MCQs
        })
    return jsonify({
        "id": quiz.id,
        "title": quiz.title,
        "description": quiz.description,
        "course_id": quiz.course_id,
        "lecture_id": quiz.lecture_id,
        "questions": questions_output
    }), 200

@quiz_bp.route("/quizzes/<int:quiz_id>/submit", methods=["POST"])
def submit_quiz_answers(quiz_id):
    if "user_id" not in session:
        return jsonify({"error": "يرجى تسجيل الدخول لتقديم إجابات الاختبار."}), 401

    user_id = session["user_id"]
    data = request.get_json()
    answers = data.get("answers") # Expected format: [{ "question_id": X, "answer_text": "Y" }, ...]

    if not answers or not isinstance(answers, list):
        return jsonify({"error": "صيغة الإجابات غير صحيحة."}), 400

    # Basic validation and scoring (can be made more complex)
    score = 0
    total_questions = 0

    for ans_data in answers:
        question_id = ans_data.get("question_id")
        answer_text = ans_data.get("answer_text")
        
        question = Question.query.get(question_id)
        if not question or question.quiz_id != quiz_id:
            # Skip if question not found or doesn't belong to this quiz
            continue 
        
        total_questions += 1
        is_correct = False
        if question.question_type == "multiple_choice":
            # Assuming correct_answer stores the key of the correct option, e.g., "C"
            if answer_text == question.correct_answer:
                is_correct = True
        # Add logic for other question types (true_false, short_answer - might need fuzzy matching for short_answer)
        else: # For simplicity, direct comparison for other types for now
            if answer_text and question.correct_answer and answer_text.strip().lower() == question.correct_answer.strip().lower():
                is_correct = True

        if is_correct:
            score += 1

        student_answer = StudentAnswer(
            user_id=user_id,
            question_id=question_id,
            quiz_id=quiz_id,
            answer_text=answer_text,
            is_correct=is_correct
        )
        db.session.add(student_answer)
    
    try:
        db.session.commit()
        return jsonify({
            "message": "تم تقديم إجاباتك بنجاح!", 
            "score": score, 
            "total_questions": total_questions
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"حدث خطأ أثناء تقديم الإجابات: {str(e)}"}), 500


