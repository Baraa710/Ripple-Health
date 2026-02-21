from flask import Blueprint, request, jsonify, g
from models.user import User
from extensions import get_db
from xrpl_utils.xrpl_utils import create_account
import sqlite3
users_bp = Blueprint('users', __name__)

@users_bp.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    user_type = data.get('user_type')  # 'doctor', 'patient', or 'donor'
    
    if not all([name, email, user_type]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Create XRPL account
    wallet = create_account()
    account_address = wallet.address
    
    # Create User instance
    user = User(user_id=None, name=name, email=email, user_type=user_type)
    user.account_address = account_address
    
    # Save to DB
    db = get_db()
    try:
        cursor = db.execute('INSERT INTO users (name, email, account_address, user_type) VALUES (?, ?, ?, ?)',
                            (user.name, user.email, user.account_address, user.user_type))
        db.commit()
        user.user_id = cursor.lastrowid
        return jsonify(user.to_dict()), 201
    except sqlite3.IntegrityError as e:
        db.rollback()
        if 'email' in str(e):
            return jsonify({'error': 'Email already registered'}), 409
        return jsonify({'error': 'Database error'}), 500

@users_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    db = get_db()
    user_row = db.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()
    if user_row:
        user = User(user_id=user_row['user_id'], name=user_row['name'], email=user_row['email'],
                    user_type=user_row['user_type'])
        user.account_address = user_row['account_address']
        user.created_at = user_row['created_at']
        return jsonify(user.to_dict()), 200
    return jsonify({'error': 'User not found'}), 404

