import os
from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from extensions import db
from xrpl_utils.xrpl_utils import create_account, fund_account_from_faucet
from datetime import datetime

users_bp = Blueprint("users", __name__)


@users_bp.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    user_type = data.get("user_type")
    password = data.get("password")

    if not all([name, email, user_type, password]):
        return jsonify({"error": "Missing required fields (name, email, user_type, password)"}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "Email already registered"}), 409

    wallet = create_account()

    new_user = User(
        name=name,
        email=email,
        user_type=user_type,
        password=password,
    )
    new_user.xrp_address = wallet.address
    new_user.xrp_seed = wallet.seed
    new_user.created_at = datetime.utcnow()

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
        "user_type": new_user.user_type,
        "xrp_address": new_user.xrp_address,
    }), 201


@users_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    login_user(user)
    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "user_type": user.user_type,
        "xrp_address": user.xrp_address,
        "is_verified_doctor": user.is_verified_doctor,
    }), 200


@users_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out"}), 200


@users_bp.route("/me", methods=["GET"])
@login_required
def me():
    return jsonify({
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "user_type": current_user.user_type,
        "xrp_address": current_user.xrp_address,
        "is_verified_doctor": current_user.is_verified_doctor,
    }), 200


@users_bp.route("/fund-me", methods=["POST"])
@login_required
def fund_my_account():
    """
    Fund the current user's XRP address from the testnet faucet.
    Only works on testnet; requires login.
    """
    ok, msg = fund_account_from_faucet(current_user.xrp_seed)
    if ok:
        return jsonify({"message": msg, "xrp_address": current_user.xrp_address}), 200
    return jsonify({"error": msg}), 502


@users_bp.route("/users/verified", methods=["GET"])
def list_verified_doctors():
    doctors = User.query.filter_by(user_type="doctor", is_verified_doctor=True).all()
    return jsonify({
        "doctors": [
            {"id": u.id, "name": u.name, "email": u.email, "xrp_address": u.xrp_address}
            for u in doctors
        ]
    }), 200


@users_bp.route("/users/<int:user_id>/verify", methods=["PUT"])
@login_required
def verify_doctor(user_id):
    admin_email = os.environ.get("ADMIN_EMAIL")
    if not admin_email or current_user.email != admin_email:
        return jsonify({"error": "Only admin can verify doctors"}), 403

    user = User.query.get_or_404(user_id)
    if user.user_type != "doctor":
        return jsonify({"error": "Only doctors can be verified"}), 400
    user.is_verified_doctor = True
    db.session.commit()
    return jsonify({"message": "Doctor verified", "user_id": user_id}), 200


@users_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "user_type": user.user_type,
        "xrp_address": user.xrp_address,
        "is_verified_doctor": user.is_verified_doctor,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }), 200