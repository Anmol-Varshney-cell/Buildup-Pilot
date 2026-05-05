from app import app
from models import User
from extensions import db
from flask import request, session

# Create a simple test to isolate the admin dashboard issue
with app.test_client() as client:
    # Test login first
    response = client.post('/auth/login', data={
        'email': 'admin@buildup.com',
        'password': 'admin123'
    }, follow_redirects=True)
    
    print(f"Login response status: {response.status_code}")
    print(f"Login response data length: {len(response.data)}")
    
    # Now test admin dashboard
    response = client.get('/admin/dashboard')
    print(f"Admin dashboard response status: {response.status_code}")
    
    if response.status_code == 500:
        print("500 Internal Server Error detected")
        print("Response data:")
        print(response.get_data(as_text=True))
    else:
        print("Admin dashboard loaded successfully")
        print(f"Response data length: {len(response.data)}")
