from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS
from flask_session import Session
import redis
import os

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Initialize Redis session store (required for 5000-6000 concurrent users)
# Fallback to simple signed cookie sessions if Redis is unavailable
try:
    redis_client = redis.from_url(Config.REDIS_URL)
    redis_client.ping()  # Test connection
    app.config['SESSION_REDIS'] = redis_client
    Session(app)
    print("✓ Redis session store initialized")
except redis.ConnectionError as e:
    print(f"[WARN] Redis unavailable ({e}), using built-in signed cookie sessions instead")
    # Use built-in Flask sessions (default signed cookies, no external store)
    # Set secret key for signed cookies
    app.secret_key = Config.SECRET_KEY

# Configure CORS
CORS(app, origins=[
    'http://localhost:5173', 'http://127.0.0.1:5173',
    'http://localhost:5174', 'http://127.0.0.1:5174'
], supports_credentials=True)

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

# Create database tables and register blueprints
with app.app_context():
    db.create_all()
    from routes import main, auth, student, admin, recruiter, api
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(student)
    app.register_blueprint(admin)
    app.register_blueprint(recruiter)
    app.register_blueprint(api)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    app.run(debug=True, port=port)
