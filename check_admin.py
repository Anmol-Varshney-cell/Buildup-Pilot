from app import app
from models import User
from extensions import db
from flask_bcrypt import check_password_hash

with app.app_context():
    admin_user = User.query.filter_by(email='admin@buildup.com').first()
    print(f'Admin user found: {admin_user.email if admin_user else None}')
    if admin_user:
        print(f'Role: {admin_user.role}')
        print(f'Password hash: {admin_user.password_hash[:50]}...')
        print(f'ID: {admin_user.id}')
        # Test with common passwords
        test_passwords = ['admin', 'admin123', 'password', 'buildup', 'admin@123']
        for pwd in test_passwords:
            try:
                result = check_password_hash(admin_user.password_hash, pwd)
                print(f'Password "{pwd}": {result}')
                if result:
                    print(f'  -> FOUND CORRECT PASSWORD: {pwd}')
                    break
            except Exception as e:
                print(f'Error testing "{pwd}": {e}')
    else:
        print('No admin user found in database')
