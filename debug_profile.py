
from app import app
from models import User, StudentProfile
with app.app_context():
    users = User.query.filter(User.role == 'student').all()
    print("=== USERS ===")
    for u in users:
        profile = StudentProfile.query.filter_by(user_id=u.id).first()
        print(f"User {u.id} ({u.email}): first_name='{profile.first_name if profile else None}', skills='{profile.skills if profile else None}'")
    print("=== END ===")

