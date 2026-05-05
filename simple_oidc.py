import json
import time
import uuid
import hmac
import hashlib
import base64
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, redirect, url_for
from flask_login import current_user

simple_oidc_bp = Blueprint('simple_oidc', __name__)

# Simple OIDC Configuration
OIDC_CONFIG = {
    'issuer': 'http://localhost:5000',
    'authorization_endpoint': 'http://localhost:5000/oauth/authorize',
    'token_endpoint': 'http://localhost:5000/oauth/token',
    'userinfo_endpoint': 'http://localhost:5000/oauth/userinfo'
}

# OIDC Clients
OIDC_CLIENTS = {
    'coding-spirit-client': {
        'client_id': 'coding-spirit-client',
        'client_secret': 'coding-spirit-secret',
        'redirect_uris': ['http://localhost:5173']
    }
}

# In-memory storage (use database in production)
AUTHORIZATION_CODES = {}
ACCESS_TOKENS = {}

@simple_oidc_bp.route('/.well-known/openid-configuration')
def openid_configuration():
    """OIDC discovery endpoint"""
    return jsonify(OIDC_CONFIG)

@simple_oidc_bp.route('/oauth/authorize')
def authorize():
    """OIDC authorization endpoint"""
    client_id = request.args.get('client_id')
    redirect_uri = request.args.get('redirect_uri')
    response_type = request.args.get('response_type')
    scope = request.args.get('scope')
    state = request.args.get('state')
    
    # Validate client
    if client_id not in OIDC_CLIENTS:
        return jsonify({'error': 'invalid_client'}), 400
    
    client = OIDC_CLIENTS[client_id]
    if redirect_uri not in client['redirect_uris']:
        return jsonify({'error': 'invalid_redirect_uri'}), 400
    
    # Check if user is authenticated
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login', next=request.url))
    
    # Generate authorization code
    code = str(uuid.uuid4())
    AUTHORIZATION_CODES[code] = {
        'client_id': client_id,
        'user_id': current_user.id,
        'redirect_uri': redirect_uri,
        'expires_at': datetime.utcnow() + timedelta(minutes=10),
        'user_data': {
            'sub': str(current_user.id),
            'email': current_user.email,
            'name': current_user.email.split('@')[0] if current_user.email else 'User'
        }
    }
    
    # Redirect back to client
    callback_url = f"{redirect_uri}?code={code}"
    if state:
        callback_url += f"&state={state}"
    
    return redirect(callback_url)

@simple_oidc_bp.route('/oauth/token', methods=['POST'])
def token():
    """OIDC token endpoint"""
    grant_type = request.form.get('grant_type')
    
    if grant_type != 'authorization_code':
        return jsonify({'error': 'unsupported_grant_type'}), 400
    
    code = request.form.get('code')
    client_id = request.form.get('client_id')
    client_secret = request.form.get('client_secret')
    
    # Validate client
    if client_id not in OIDC_CLIENTS:
        return jsonify({'error': 'invalid_client'}), 401
    
    client = OIDC_CLIENTS[client_id]
    if client['client_secret'] != client_secret:
        return jsonify({'error': 'invalid_client'}), 401
    
    # Validate authorization code
    if code not in AUTHORIZATION_CODES:
        return jsonify({'error': 'invalid_grant'}), 400
    
    auth_code_data = AUTHORIZATION_CODES[code]
    if datetime.utcnow() > auth_code_data['expires_at']:
        del AUTHORIZATION_CODES[code]
        return jsonify({'error': 'invalid_grant'}), 400
    
    if auth_code_data['client_id'] != client_id:
        return jsonify({'error': 'invalid_grant'}), 400
    
    # Generate tokens
    access_token = str(uuid.uuid4())
    id_token = generate_simple_id_token(auth_code_data['user_data'], client_id)
    
    # Store token
    ACCESS_TOKENS[access_token] = {
        'user_id': auth_code_data['user_id'],
        'client_id': client_id,
        'expires_at': datetime.utcnow() + timedelta(hours=1),
        'user_data': auth_code_data['user_data']
    }
    
    # Clean up authorization code
    del AUTHORIZATION_CODES[code]
    
    return jsonify({
        'access_token': access_token,
        'token_type': 'Bearer',
        'expires_in': 3600,
        'id_token': id_token
    })

@simple_oidc_bp.route('/oauth/userinfo')
def userinfo():
    """OIDC userinfo endpoint"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'invalid_token'}), 401
    
    token = auth_header[7:]  # Remove 'Bearer ' prefix
    
    if token not in ACCESS_TOKENS:
        return jsonify({'error': 'invalid_token'}), 401
    
    token_data = ACCESS_TOKENS[token]
    if datetime.utcnow() > token_data['expires_at']:
        del ACCESS_TOKENS[token]
        return jsonify({'error': 'invalid_token'}), 401
    
    return jsonify(token_data['user_data'])

@simple_oidc_bp.route('/api/auth/me')
def auth_me():
    """Simple auth endpoint for instant access"""
    # Check for simple token or create demo user
    auth_header = request.headers.get('Authorization')
    
    # Allow access without authentication for demo
    demo_user = {
        'sub': 'demo-user',
        'email': 'demo@example.com',
        'name': 'Demo User',
        'id': 1
    }
    
    # If no auth header, create a simple token
    if not auth_header or not auth_header.startswith('Bearer '):
        # Generate simple access token
        simple_token = str(uuid.uuid4())
        ACCESS_TOKENS[simple_token] = {
            'user_id': 1,
            'client_id': 'coding-spirit-client',
            'expires_at': datetime.utcnow() + timedelta(hours=24),
            'user_data': demo_user
        }
        return jsonify(demo_user)
    
    token = auth_header[7:]
    
    if token not in ACCESS_TOKENS:
        # Create new token for demo
        ACCESS_TOKENS[token] = {
            'user_id': 1,
            'client_id': 'coding-spirit-client',
            'expires_at': datetime.utcnow() + timedelta(hours=24),
            'user_data': demo_user
        }
    
    return jsonify(demo_user)

@simple_oidc_bp.route('/api/auth/login', methods=['POST'])
def simple_login():
    """Simple login endpoint"""
    data = request.get_json() or {}
    email = data.get('email')
    phone = data.get('phone')
    
    # Check if user is already authenticated from Build Up Pilot
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header[7:]
        if token in ACCESS_TOKENS:
            token_data = ACCESS_TOKENS[token]
            return jsonify({
                'access_token': token,
                'token_type': 'Bearer',
                'expires_in': 86400,
                'user': token_data['user_data']
            })
    
    # Create user data
    if email:
        user_data = {
            'sub': f'user-{email}',
            'email': email,
            'name': email.split('@')[0] if email else 'User',
            'id': hash(email) % 1000000  # Simple ID generation
        }
    elif phone:
        user_data = {
            'sub': f'user-{phone}',
            'email': f'user-{phone}@codespirit.com',
            'name': f'User-{phone[-4:]}',
            'id': hash(phone) % 1000000
        }
    else:
        user_data = {
            'sub': 'demo-user',
            'email': 'demo@example.com',
            'name': 'Demo User',
            'id': 1
        }
    
    # Generate access token
    access_token = str(uuid.uuid4())
    ACCESS_TOKENS[access_token] = {
        'user_id': user_data['id'],
        'client_id': 'coding-spirit-client',
        'expires_at': datetime.utcnow() + timedelta(hours=24),
        'user_data': user_data
    }
    
    return jsonify({
        'access_token': access_token,
        'token_type': 'Bearer',
        'expires_in': 86400,
        'user': user_data
    })

@simple_oidc_bp.route('/api/auth/signup', methods=['POST'])
def simple_signup():
    """Simple signup endpoint"""
    data = request.get_json() or {}
    email = data.get('email')
    phone = data.get('phone')
    
    if not email and not phone:
        return jsonify({'error': 'Email or phone is required'}), 400
    
    # Create user data
    if email:
        user_data = {
            'sub': f'user-{email}',
            'email': email,
            'name': email.split('@')[0] if email else 'User',
            'id': hash(email) % 1000000
        }
    else:
        user_data = {
            'sub': f'user-{phone}',
            'email': f'user-{phone}@codespirit.com',
            'name': f'User-{phone[-4:]}',
            'id': hash(phone) % 1000000
        }
    
    # Generate access token
    access_token = str(uuid.uuid4())
    ACCESS_TOKENS[access_token] = {
        'user_id': user_data['id'],
        'client_id': 'coding-spirit-client',
        'expires_at': datetime.utcnow() + timedelta(hours=24),
        'user_data': user_data
    }
    
    return jsonify({
        'access_token': access_token,
        'token_type': 'Bearer',
        'expires_in': 86400,
        'user': user_data
    })

@simple_oidc_bp.route('/api/problems')
def get_problems():
    """Get coding problems from FastAPI backend"""
    try:
        import requests
        
        # Forward request to FastAPI backend
        backend_url = "http://localhost:8000/api/problems"
        response = requests.get(backend_url, params=request.args)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Failed to fetch problems'}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@simple_oidc_bp.route('/api/problems/<slug>')
def get_problem_detail(slug):
    """Get problem detail from FastAPI backend"""
    try:
        import requests
        
        # Forward request to FastAPI backend
        backend_url = f"http://localhost:8000/api/problems/{slug}"
        response = requests.get(backend_url)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Problem not found'}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@simple_oidc_bp.route('/api/submissions/execute', methods=['POST'])
def execute_code():
    """Execute code via FastAPI backend"""
    try:
        import requests
        
        # Forward request to FastAPI backend
        backend_url = "http://localhost:8000/api/submissions/execute"
        response = requests.post(backend_url, json=request.get_json())
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Execution failed'}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@simple_oidc_bp.route('/api/test-login', methods=['POST'])
def test_login():
    """Test login endpoint for development"""
    try:
        from flask import session
        data = request.get_json()
        
        # Store test user in session
        session['user_id'] = data.get('user_id', 'test-user-1')
        
        # Store user data for frontend
        test_user = {
            'id': data.get('user_id', 'test-user-1'),
            'email': data.get('email', 'test@example.com'),
            'name': data.get('name', 'Test User'),
            'createdAt': '2024-01-01',
            'totalProblemsSolved': 0,
            'languageStats': []
        }
        
        return jsonify({
            'success': True,
            'user': test_user
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@simple_oidc_bp.route('/api/profile/me')
def get_profile():
    """Get current user profile from BUILD UP PILOT session"""
    try:
        from flask import session
        # Get user from session
        if 'user_id' in session:
            user_id = session['user_id']
            
            # Get user from database (assuming buildup.db has users table)
            import sqlite3
            conn = sqlite3.connect('buildup.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, name, created_at FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return jsonify({
                    'user': {
                        'id': user[0],
                        'email': user[1], 
                        'name': user[2],
                        'createdAt': user[3],
                        'totalProblemsSolved': 0,  # Default values for now
                        'languageStats': []  # Default values for now
                    }
                })
            else:
                # Return test user if no database user found
                return jsonify({
                    'user': {
                        'id': user_id,
                        'email': 'test@example.com',
                        'name': 'Test User',
                        'createdAt': '2024-01-01',
                        'totalProblemsSolved': 0,
                        'languageStats': []
                    }
                })
        else:
            return jsonify({'error': 'Not authenticated'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_simple_id_token(user_data, client_id):
    """Generate simple ID token (not real JWT, but functional)"""
    payload = {
        'iss': OIDC_CONFIG['issuer'],
        'sub': user_data['sub'],
        'aud': client_id,
        'exp': int(time.time()) + 3600,
        'iat': int(time.time()),
        'email': user_data['email'],
        'name': user_data['name']
    }
    
    # Simple token (not real JWT, but works for demo)
    payload_str = json.dumps(payload, separators=(',', ':'))
    payload_b64 = base64.urlsafe_b64encode(payload_str.encode('utf-8')).decode('utf-8').rstrip('=')
    signature = hmac.new('simple-secret'.encode('utf-8'), payload_b64.encode('utf-8'), hashlib.sha256).hexdigest()
    
    return f'{payload_b64}.{signature}'
