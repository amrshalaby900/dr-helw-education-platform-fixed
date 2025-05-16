import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS # Import CORS
from src.models.user import db, User # Import User model
from werkzeug.security import generate_password_hash # Import password hashing function
from src.routes.user import user_bp
from src.routes.course import course_bp
from src.routes.quiz import quiz_bp
from src.routes.forum_announcement import forum_announcement_bp
from src.routes.progress import progress_bp
from src.routes.reports import reports_bp
from src.routes.email import email_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Configure CORS
CORS(
    app,
    supports_credentials=True,
    resources={r"/api/*": {"origins": "https://477h9ikcp85l.manus.space"}}
)

# Configure session cookie settings for production
app.config.update(
    SESSION_COOKIE_SECURE=True,    # Send cookie only over HTTPS
    SESSION_COOKIE_HTTPONLY=True,  # Prevent client-side JavaScript access
    SESSION_COOKIE_SAMESITE='None', # Allow cross-origin cookie sending (requires Secure=True)
    PERMANENT_SESSION_LIFETIME=2592000, # 30 days in seconds (30 * 24 * 60 * 60)
    # SESSION_COOKIE_DOMAIN='.manus.space' # Optional: if you need cookies across subdomains
)

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(course_bp, url_prefix='/api')
app.register_blueprint(quiz_bp, url_prefix='/api')
app.register_blueprint(forum_announcement_bp, url_prefix='/api')
app.register_blueprint(progress_bp, url_prefix='/api')
app.register_blueprint(reports_bp, url_prefix='/api')
app.register_blueprint(email_bp, url_prefix='/api')

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'mydb')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

    # Create admin user if not exists
    admin_username = "MohamedElhelw"
    admin_password = "MohamedElhelw500Dr00$"
    admin_email = "admin@example.com" # Placeholder email
    admin_full_name = "Admin Elhelw" # Placeholder full name

    existing_admin = User.query.filter_by(username=admin_username).first()
    if not existing_admin:
        hashed_password = generate_password_hash(admin_password)
        new_admin = User(
            username=admin_username,
            email=admin_email,
            password_hash=hashed_password,
            full_name=admin_full_name,
            is_admin=True
        )
        db.session.add(new_admin)
        db.session.commit()
        print(f"Admin user '{admin_username}' created successfully.")
    else:
        print(f"Admin user '{admin_username}' already exists.")


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
