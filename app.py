from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'build-up-secret-key-2024'
    PORTAL_SSO_SECRET = os.environ.get('PORTAL_SSO_SECRET') or SECRET_KEY
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'buildup.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY') or ''
    ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY') or ''

app = Flask(__name__)
app.config.from_object(Config)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Configure CORS
CORS(app, origins=['http://localhost:5173', 'http://127.0.0.1:5173', 'http://localhost:5174', 'http://127.0.0.1:5174'], supports_credentials=True)

from extensions import db, bcrypt
db.init_app(app)
bcrypt.init_app(app)

# Import and register simple OIDC provider
from simple_oidc import simple_oidc_bp
app.register_blueprint(simple_oidc_bp)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Import models before create_all so SQLAlchemy metadata is populated.
import models  # noqa: F401

with app.app_context():
    db.create_all()
    columns_to_add = [
        ("users", "student_id VARCHAR(20)"),
        ("users", "mobile VARCHAR(15)"),
        ("users", "otp VARCHAR(6)"),
        ("users", "otp_expires DATETIME"),
        ("users", "is_verified BOOLEAN DEFAULT 0"),
        ("student_profiles", "profession VARCHAR(100)"),
        ("student_profiles", "profile_image_path VARCHAR(200)"),
        ("student_profiles", "portfolio_file_path VARCHAR(200)"),
        ("student_profiles", "weak_areas TEXT"),
        ("jobs", "work_mode VARCHAR(20) DEFAULT 'onsite'"),
        ("jobs", "stipend INTEGER"),
        ("skill_tests", "correct_answers INTEGER DEFAULT 0"),
        ("skill_tests", "wrong_answers INTEGER DEFAULT 0"),
        ("skill_tests", "tab_switches INTEGER DEFAULT 0"),
        ("skill_tests", "ai_detected BOOLEAN DEFAULT 0"),
        ("skill_tests", "weak_topics TEXT"),
        ("skill_tests", "question_order TEXT"),
        ("skill_tests", "user_id INTEGER"),
        ("test_questions", "topic VARCHAR(100)"),
        ("certificates", "score INTEGER"),
        ("certificates", "certificate_id VARCHAR(50)"),
        ("certificates", "issued_by VARCHAR(100)"),
        ("certificates", "validity_date DATETIME"),
        ("certificates", "status VARCHAR(20) DEFAULT 'active'"),
        ("mock_interviews", "proctoring_logs TEXT"),
        ("communication_practices", "user_id INTEGER"),
        ("communication_practices", "practice_type VARCHAR(20)"),
        ("communication_practices", "topic VARCHAR(200)"),
        ("communication_practices", "content TEXT"),
        ("communication_practices", "duration INTEGER DEFAULT 0"),
        ("communication_practices", "clarity_rating INTEGER DEFAULT 0"),
        ("communication_practices", "structure_rating INTEGER DEFAULT 0"),
        ("communication_practices", "confidence_rating INTEGER DEFAULT 0"),
        ("communication_practices", "created_at DATETIME"),
    ]
    
    for table, column_def in columns_to_add:
        try:
            db.session.execute(db.text(f"ALTER TABLE {table} ADD COLUMN {column_def}"))
            db.session.commit()
        except Exception:
            pass
    
    try:
        from models import User
        users = User.query.order_by(User.id.asc()).all()
        for user in users:
            expected_student_id = f'BUP{int(user.id):03d}'
            if user.role == 'student' and user.student_id != expected_student_id:
                user.student_id = expected_student_id
        db.session.commit()
    except Exception:
        db.session.rollback()

from routes import main, auth, student, admin, recruiter, api
app.register_blueprint(main)
app.register_blueprint(auth)
app.register_blueprint(student)
app.register_blueprint(admin)
app.register_blueprint(recruiter)
app.register_blueprint(api)

if __name__ == '__main__':
    # Allow running on a port specified by environment variable PORT (default 5002)
    port = int(os.environ.get('PORT', 5002))
    app.run(debug=True, port=port)
