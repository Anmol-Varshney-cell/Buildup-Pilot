from app import app
from models import User
from extensions import db
from flask_bcrypt import check_password_hash
import bcrypt

with app.app_context():
    user = User.query.filter_by(email='student@buildup.com').first()
    print(f'User found: {user.email if user else None}')
    if user:
        print(f'Password hash: {user.password_hash[:50]}...')
        print(f'Testing password "student123":')
        try:
            result1 = check_password_hash(user.password_hash, 'student123')
            print(f'Flask-Bcrypt check: {result1}')
        except Exception as e:
            print(f'Flask-Bcrypt error: {e}')
        
        try:
            result2 = bcrypt.check_password_hash(user.password_hash, 'student123')
            print(f'Direct bcrypt check: {result2}')
        except Exception as e:
            print(f'Direct bcrypt error: {e}')
            
        # Test with wrong password
        print(f'Testing wrong password:')
        try:
            result3 = check_password_hash(user.password_hash, 'wrongpass')
            print(f'Wrong password check: {result3}')
        except Exception as e:
            print(f'Wrong password error: {e}')
