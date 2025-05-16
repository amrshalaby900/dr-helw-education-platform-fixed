from flask import Blueprint, request, jsonify, session, render_template, url_for
from src.models.user import db, User
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import secrets
import datetime

email_bp = Blueprint("email_routes", __name__)

# إعدادات البريد الإلكتروني
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', 'your-email@gmail.com')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', 'your-password')
SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'no-reply@drmohamedelhelw.com')
SENDER_NAME = os.getenv('SENDER_NAME', 'منصة دكتور محمد الحلو التعليمية')

def send_email(recipient, subject, html_content, text_content=None):
    """
    إرسال بريد إلكتروني
    """
    if not text_content:
        text_content = "يرجى استخدام متصفح يدعم HTML لعرض هذه الرسالة."
    
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
    message["To"] = recipient
    
    # إضافة محتوى النص العادي والـ HTML
    part1 = MIMEText(text_content, "plain", "utf-8")
    part2 = MIMEText(html_content, "html", "utf-8")
    
    message.attach(part1)
    message.attach(part2)
    
    try:
        # إنشاء اتصال SMTP آمن
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        
        # إرسال البريد الإلكتروني
        server.sendmail(SENDER_EMAIL, recipient, message.as_string())
        server.quit()
        return True, "تم إرسال البريد الإلكتروني بنجاح"
    except Exception as e:
        return False, f"فشل إرسال البريد الإلكتروني: {str(e)}"

@email_bp.route("/send-notification", methods=["POST"])
def send_notification_email():
    """
    إرسال إشعار عبر البريد الإلكتروني
    """
    if not session.get("user_id") or not session.get("is_admin"):
        return jsonify({"error": "غير مصرح لك بالقيام بهذه العملية"}), 403
    
    data = request.get_json()
    recipients = data.get("recipients", [])
    subject = data.get("subject", "إشعار من منصة دكتور محمد الحلو التعليمية")
    message = data.get("message", "")
    
    if not recipients or not message:
        return jsonify({"error": "يرجى تحديد المستلمين ومحتوى الرسالة"}), 400
    
    # إنشاء قالب HTML للإشعار
    html_content = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>{subject}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f9f9f9;
                direction: rtl;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                text-align: center;
                padding-bottom: 20px;
                border-bottom: 1px solid #eee;
            }}
            .header h1 {{
                color: #4CAF50;
                margin: 0;
                font-size: 24px;
            }}
            .content {{
                padding: 20px 0;
                line-height: 1.6;
            }}
            .footer {{
                text-align: center;
                padding-top: 20px;
                border-top: 1px solid #eee;
                color: #777;
                font-size: 12px;
            }}
            .button {{
                display: inline-block;
                background-color: #4CAF50;
                color: white;
                text-decoration: none;
                padding: 10px 20px;
                border-radius: 5px;
                margin-top: 15px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{subject}</h1>
            </div>
            <div class="content">
                {message}
            </div>
            <div class="footer">
                <p>هذه رسالة آلية من منصة دكتور محمد الحلو التعليمية، يرجى عدم الرد عليها.</p>
                <p>&copy; {datetime.datetime.now().year} منصة دكتور محمد الحلو التعليمية. جميع الحقوق محفوظة.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # إرسال البريد الإلكتروني لكل مستلم
    results = []
    for recipient in recipients:
        success, message = send_email(recipient, subject, html_content)
        results.append({"email": recipient, "success": success, "message": message})
    
    return jsonify({"results": results}), 200

@email_bp.route("/reset-password", methods=["POST"])
def request_password_reset():
    """
    طلب إعادة تعيين كلمة المرور
    """
    data = request.get_json()
    email = data.get("email")
    
    if not email:
        return jsonify({"error": "يرجى إدخال البريد الإلكتروني"}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user:
        # لأسباب أمنية، نعيد رسالة نجاح حتى لو لم يكن البريد الإلكتروني موجوداً
        return jsonify({"message": "إذا كان البريد الإلكتروني مسجلاً، سيتم إرسال رابط إعادة تعيين كلمة المرور"}), 200
    
    # إنشاء رمز إعادة تعيين كلمة المرور
    reset_token = secrets.token_urlsafe(32)
    user.reset_token = reset_token
    user.reset_token_expiry = datetime.datetime.now() + datetime.timedelta(hours=24)
    
    try:
        db.session.commit()
        
        # إنشاء رابط إعادة تعيين كلمة المرور
        reset_url = f"https://477h9ikcp85l.manus.space/reset-password?token={reset_token}"
        
        # إنشاء قالب HTML لإعادة تعيين كلمة المرور
        html_content = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <title>إعادة تعيين كلمة المرور</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f9f9f9;
                    direction: rtl;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    text-align: center;
                    padding-bottom: 20px;
                    border-bottom: 1px solid #eee;
                }}
                .header h1 {{
                    color: #4CAF50;
                    margin: 0;
                    font-size: 24px;
                }}
                .content {{
                    padding: 20px 0;
                    line-height: 1.6;
                }}
                .footer {{
                    text-align: center;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    color: #777;
                    font-size: 12px;
                }}
                .button {{
                    display: inline-block;
                    background-color: #4CAF50;
                    color: white;
                    text-decoration: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    margin-top: 15px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>إعادة تعيين كلمة المرور</h1>
                </div>
                <div class="content">
                    <p>مرحباً {user.full_name or user.username}،</p>
                    <p>لقد تلقينا طلباً لإعادة تعيين كلمة المرور الخاصة بحسابك. إذا لم تقم بهذا الطلب، يرجى تجاهل هذه الرسالة.</p>
                    <p>لإعادة تعيين كلمة المرور، يرجى النقر على الرابط أدناه:</p>
                    <p style="text-align: center;">
                        <a href="{reset_url}" class="button">إعادة تعيين كلمة المرور</a>
                    </p>
                    <p>أو نسخ الرابط التالي ولصقه في متصفحك:</p>
                    <p style="direction: ltr; text-align: center;">{reset_url}</p>
                    <p>ينتهي هذا الرابط خلال 24 ساعة.</p>
                </div>
                <div class="footer">
                    <p>هذه رسالة آلية من منصة دكتور محمد الحلو التعليمية، يرجى عدم الرد عليها.</p>
                    <p>&copy; {datetime.datetime.now().year} منصة دكتور محمد الحلو التعليمية. جميع الحقوق محفوظة.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # إرسال البريد الإلكتروني
        success, message = send_email(user.email, "إعادة تعيين كلمة المرور", html_content)
        
        if success:
            return jsonify({"message": "تم إرسال رابط إعادة تعيين كلمة المرور إلى بريدك الإلكتروني"}), 200
        else:
            return jsonify({"error": "حدث خطأ أثناء إرسال البريد الإلكتروني"}), 500
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"حدث خطأ أثناء معالجة طلبك: {str(e)}"}), 500

@email_bp.route("/reset-password/<token>", methods=["POST"])
def reset_password(token):
    """
    إعادة تعيين كلمة المرور باستخدام الرمز
    """
    data = request.get_json()
    new_password = data.get("new_password")
    
    if not new_password:
        return jsonify({"error": "يرجى إدخال كلمة المرور الجديدة"}), 400
    
    user = User.query.filter_by(reset_token=token).first()
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.datetime.now():
        return jsonify({"error": "رمز إعادة تعيين كلمة المرور غير صالح أو منتهي الصلاحية"}), 400
    
    # تحديث كلمة المرور
    user.password_hash = generate_password_hash(new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    
    try:
        db.session.commit()
        return jsonify({"message": "تم إعادة تعيين كلمة المرور بنجاح"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"حدث خطأ أثناء إعادة تعيين كلمة المرور: {str(e)}"}), 500
