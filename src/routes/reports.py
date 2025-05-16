from flask import Blueprint, request, jsonify, session, render_template, make_response
from src.models.user import db, User
import pdfkit
from datetime import datetime
from weasyprint import HTML, CSS
from io import BytesIO
import tempfile
import os

reports_bp = Blueprint("reports_routes", __name__)

@reports_bp.route("/reports", methods=["GET"])
def get_reports():
    """الحصول على قائمة التقارير المتاحة"""
    if not session.get("user_id"):
        return jsonify({"error": "يجب تسجيل الدخول للوصول إلى التقارير"}), 401
    
    # هنا يمكن استرجاع التقارير من قاعدة البيانات
    # هذه بيانات تجريبية للعرض
    reports = [
        {"id": 1, "title": "تقرير أداء الطلاب - الفصل الأول", "type": "students", "date": "2025-05-01", "status": "completed"},
        {"id": 2, "title": "تقرير حضور المحاضرات", "type": "students", "date": "2025-05-05", "status": "active"},
        {"id": 3, "title": "تقرير نتائج الاختبارات النصفية", "type": "quizzes", "date": "2025-04-20", "status": "completed"},
        {"id": 4, "title": "تقرير تقدم المقررات", "type": "courses", "date": "2025-05-10", "status": "active"}
    ]
    
    return jsonify({"reports": reports}), 200

@reports_bp.route("/reports/<int:report_id>", methods=["GET"])
def get_report(report_id):
    """الحصول على تفاصيل تقرير محدد"""
    if not session.get("user_id"):
        return jsonify({"error": "يجب تسجيل الدخول للوصول إلى التقارير"}), 401
    
    # هنا يمكن استرجاع التقرير من قاعدة البيانات
    # هذه بيانات تجريبية للعرض
    report = {
        "id": report_id,
        "title": f"تقرير رقم {report_id}",
        "type": "students",
        "date": "2025-05-01",
        "status": "completed",
        "content": "محتوى التقرير التفصيلي هنا..."
    }
    
    return jsonify({"report": report}), 200

@reports_bp.route("/reports/export/<int:report_id>", methods=["GET"])
def export_report_pdf(report_id):
    """تصدير تقرير محدد بصيغة PDF"""
    if not session.get("user_id"):
        return jsonify({"error": "يجب تسجيل الدخول لتصدير التقارير"}), 401
    
    # استرجاع بيانات التقرير (تجريبي)
    report = {
        "id": report_id,
        "title": f"تقرير رقم {report_id}",
        "type": "students",
        "date": "2025-05-01",
        "status": "completed",
        "content": "محتوى التقرير التفصيلي هنا..."
    }
    
    # إنشاء قالب HTML للتقرير
    html_content = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>{report['title']}</title>
        <style>
            @font-face {{
                font-family: 'Noto Sans Arabic';
                src: url('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc');
            }}
            body {{
                font-family: 'Noto Sans Arabic', 'WenQuanYi Zen Hei', sans-serif;
                padding: 20px;
                direction: rtl;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .report-title {{
                font-size: 24px;
                color: #333;
                margin-bottom: 10px;
            }}
            .report-meta {{
                font-size: 14px;
                color: #666;
                margin-bottom: 20px;
            }}
            .report-content {{
                font-size: 16px;
                line-height: 1.6;
            }}
            .footer {{
                margin-top: 50px;
                text-align: center;
                font-size: 12px;
                color: #999;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1 class="report-title">{report['title']}</h1>
            <div class="report-meta">
                <p>نوع التقرير: {report['type']}</p>
                <p>تاريخ التقرير: {report['date']}</p>
                <p>الحالة: {report['status']}</p>
            </div>
        </div>
        
        <div class="report-content">
            {report['content']}
        </div>
        
        <div class="footer">
            <p>تم إنشاء هذا التقرير بواسطة منصة دكتور محمد الحلو التعليمية</p>
            <p>تاريخ التصدير: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </body>
    </html>
    """
    
    # إنشاء ملف PDF باستخدام WeasyPrint
    pdf = HTML(string=html_content).write_pdf()
    
    # إنشاء استجابة مع ملف PDF
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=report_{report_id}.pdf'
    
    return response

@reports_bp.route("/reports/export-all", methods=["POST"])
def export_all_reports_pdf():
    """تصدير مجموعة من التقارير بصيغة PDF"""
    if not session.get("user_id"):
        return jsonify({"error": "يجب تسجيل الدخول لتصدير التقارير"}), 401
    
    data = request.get_json()
    report_ids = data.get("report_ids", [])
    
    if not report_ids:
        return jsonify({"error": "لم يتم تحديد أي تقارير للتصدير"}), 400
    
    # استرجاع بيانات التقارير (تجريبي)
    reports = []
    for report_id in report_ids:
        reports.append({
            "id": report_id,
            "title": f"تقرير رقم {report_id}",
            "type": "students",
            "date": "2025-05-01",
            "status": "completed",
            "content": f"محتوى التقرير التفصيلي للتقرير رقم {report_id}..."
        })
    
    # إنشاء قالب HTML للتقارير المجمعة
    html_content = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>تقارير منصة دكتور محمد الحلو التعليمية</title>
        <style>
            @font-face {{
                font-family: 'Noto Sans Arabic';
                src: url('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc');
            }}
            body {{
                font-family: 'Noto Sans Arabic', 'WenQuanYi Zen Hei', sans-serif;
                padding: 20px;
                direction: rtl;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .main-title {{
                font-size: 28px;
                color: #333;
                margin-bottom: 20px;
            }}
            .report {{
                margin-bottom: 50px;
                page-break-after: always;
            }}
            .report-title {{
                font-size: 24px;
                color: #333;
                margin-bottom: 10px;
                border-bottom: 1px solid #ddd;
                padding-bottom: 5px;
            }}
            .report-meta {{
                font-size: 14px;
                color: #666;
                margin-bottom: 20px;
            }}
            .report-content {{
                font-size: 16px;
                line-height: 1.6;
            }}
            .footer {{
                margin-top: 50px;
                text-align: center;
                font-size: 12px;
                color: #999;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1 class="main-title">تقارير منصة دكتور محمد الحلو التعليمية</h1>
            <p>عدد التقارير: {len(reports)}</p>
            <p>تاريخ التصدير: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    """
    
    # إضافة محتوى كل تقرير
    for report in reports:
        html_content += f"""
        <div class="report">
            <h2 class="report-title">{report['title']}</h2>
            <div class="report-meta">
                <p>نوع التقرير: {report['type']}</p>
                <p>تاريخ التقرير: {report['date']}</p>
                <p>الحالة: {report['status']}</p>
            </div>
            
            <div class="report-content">
                {report['content']}
            </div>
        </div>
        """
    
    # إضافة تذييل الصفحة
    html_content += """
        <div class="footer">
            <p>تم إنشاء هذا التقرير بواسطة منصة دكتور محمد الحلو التعليمية</p>
        </div>
    </body>
    </html>
    """
    
    # إنشاء ملف PDF باستخدام WeasyPrint
    pdf = HTML(string=html_content).write_pdf()
    
    # إنشاء استجابة مع ملف PDF
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=reports.pdf'
    
    return response
