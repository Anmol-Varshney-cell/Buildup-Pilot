from app import app
from models import User
from extensions import db

with app.app_context():
    users = User.query.all()
    print(f'Total users: {len(users)}')
    for user in users:
        print(f'Email: {user.email}, Role: {user.role}, ID: {user.id}')
        if user.email == 'student@buildup.com':
            print(f'  -> Demo user found! Student ID: {user.student_id}')
