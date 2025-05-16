# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.user import db, User, AccessCode
import uuid # For generating unique codes

user_bp = Blueprint("user_routes", __name__)

@user_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    access_code_value = data.get("access_code")
    full_name = data.get("full_name", "")

    if not all([username, email, password, access_code_value]):
        return jsonify({"error": "يرجى ملء جميع الحقول المطلوبة وكود الدعوة."}), 400

    access_code = AccessCode.query.filter_by(code_value=access_code_value, is_used=False).first()
    if not access_code:
        return jsonify({"error": "كود الدعوة غير صحيح أو تم استخدامه بالفعل."}), 403

    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({"error": "اسم المستخدم أو البريد الإلكتروني مسجل بالفعل."}), 409

    hashed_password = generate_password_hash(password)
    new_user = User(
        username=username, 
        email=email, 
        password_hash=hashed_password, 
        full_name=full_name
    )
    
    db.session.add(new_user)
    db.session.flush() # To get the new_user.id before committing

    access_code.is_used = True
    access_code.used_by_user_id = new_user.id
    db.session.add(access_code)
    
    try:
        db.session.commit()
        return jsonify({"message": "تم تسجيل المستخدم بنجاح!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"حدث خطأ أثناء التسجيل: {str(e)}"}), 500

@user_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    identifier = data.get("identifier") # Can be username or email
    password = data.get("password")

    if not identifier or not password:
        return jsonify({"error": "يرجى إدخال اسم المستخدم/البريد الإلكتروني وكلمة المرور."}), 400

    user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()

    if user and check_password_hash(user.password_hash, password):
        # Set session as permanent to last for 30 days
        session.permanent = True
        session["user_id"] = user.id
        session["username"] = user.username
        session["is_admin"] = user.is_admin
        return jsonify({
            "message": "تم تسجيل الدخول بنجاح!", 
            "user": {"username": user.username, "email": user.email, "full_name": user.full_name, "is_admin": user.is_admin}
        }), 200
    else:
        return jsonify({"error": "بيانات الاعتماد غير صحيحة."}), 401

@user_bp.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    session.pop("is_admin", None)
    return jsonify({"message": "تم تسجيل الخروج بنجاح."}), 200

@user_bp.route("/check_session", methods=["GET"])
def check_session():
    if "user_id" in session:
        return jsonify({
            "logged_in": True, 
            "user": {"username": session.get("username"), "is_admin": session.get("is_admin")}
        }), 200
    return jsonify({"logged_in": False}), 200

# --- Admin Routes for Code Generation ---
@user_bp.route("/admin/generate_code", methods=["POST"])
def generate_access_code():
    # Basic protection: check if user is admin (assuming session is set up)
    if not session.get("is_admin"):
        return jsonify({"error": "غير مصرح لك بالقيام بهذه العملية."}), 403
    
    new_code_value = str(uuid.uuid4())[:8] # Generate a short unique code
    while AccessCode.query.filter_by(code_value=new_code_value).first():
        new_code_value = str(uuid.uuid4())[:8]
        
    access_code = AccessCode(code_value=new_code_value)
    db.session.add(access_code)
    try:
        db.session.commit()
        return jsonify({"message": "تم إنشاء كود دعوة جديد بنجاح.", "code": new_code_value}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"حدث خطأ أثناء إنشاء الكود: {str(e)}"}), 500

@user_bp.route("/admin/codes", methods=["GET"])
def list_access_codes():
    if not session.get("is_admin"):
        return jsonify({"error": "غير مصرح لك بالقيام بهذه العملية."}), 403

    codes = AccessCode.query.all()
    output = []
    for code in codes:
        output.append({
            "id": code.id,
            "code_value": code.code_value,
            "is_used": code.is_used,
            "creation_date": code.creation_date.strftime("%Y-%m-%d %H:%M:%S") if code.creation_date else None,
            "used_by_user_id": code.used_by_user_id
        })
    return jsonify({"codes": output}), 200


