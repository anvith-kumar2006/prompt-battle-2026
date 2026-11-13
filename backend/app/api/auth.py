from flask import Blueprint, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from backend.app.extensions import db, limiter
from backend.app.models import User

bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@bp.route('/register', methods=['POST'])
@limiter.limit("5 per hour")
def register():
    """Register a new user."""
    data = request.get_json()
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    name = data.get('name', '').strip()
    role = data.get('role', 'GUARDIAN')
    phone = data.get('phone', '').strip()
    
    if not email or not password or not name:
        return jsonify({'ok': False, 'error': {'message': 'Email, password and name are required'}}), 400
    if role not in ('GUARDIAN', 'DRIVER'):
        return jsonify({'ok': False, 'error': {'message': 'Role must be GUARDIAN or DRIVER'}}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'ok': False, 'error': {'message': 'Email already registered'}}), 400
    
    user = User(
        email=email,
        password_hash=generate_password_hash(password),
        name=name,
        role=role,
        phone=phone,
        status='ACTIVE'
    )
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'ok': True,
        'data': {
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'role': user.role
            }
        }
    }), 201

@bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Authenticate user and create session."""
    data = request.get_json()
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    role = data.get('role')
    
    if not email or not password:
        return jsonify({'ok': False, 'error': {'message': 'Email and password required'}}), 400
    if role is not None and role not in ('GUARDIAN', 'DRIVER', 'STAFF'):
        return jsonify({'ok': False, 'error': {'message': 'Invalid sign-in role'}}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'ok': False, 'error': {'message': 'Invalid email or password'}}), 401
    
    allowed_roles = {
        'STAFF': ('ADMIN', 'SAFETY_ADMIN', 'OPERATOR', 'INSTITUTION_STAFF'),
    }
    if role and user.role not in allowed_roles.get(role, (role,)):
        return jsonify({
            'ok': False,
            'error': {'message': 'This account has a different role. Please choose the matching role to sign in.'}
        }), 403

    if user.status != 'ACTIVE':
        return jsonify({'ok': False, 'error': {'message': 'Account is not active'}}), 403
    
    login_user(user, remember=False)
    
    return jsonify({
        'ok': True,
        'data': {
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'role': user.role,
                'phone': user.phone
            }
        }
    }), 200

@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Log out current user."""
    logout_user()
    return jsonify({'ok': True, 'data': {'message': 'Logged out successfully'}}), 200

@bp.route('/me', methods=['GET'])
@login_required
def me():
    """Get current user info."""
    return jsonify({
        'ok': True,
        'data': {
            'user': {
                'id': current_user.id,
                'email': current_user.email,
                'name': current_user.name,
                'role': current_user.role,
                'phone': current_user.phone,
                'status': current_user.status
            }
        }
    }), 200
