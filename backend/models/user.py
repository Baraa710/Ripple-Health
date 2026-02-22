from extensions import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from xrpl_utils.xrpl_utils import create_account


class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    user_type = db.Column(db.String(50), nullable=False)  # doctor, patient, donor

    # Trust: verified doctors (charges posted by them are trusted)
    is_verified_doctor = db.Column(db.Boolean, default=False)

    # XRP Wallet Info
    xrp_address = db.Column(db.String(100), nullable=False)
    xrp_seed = db.Column(db.String(200), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships (Invoice defines doctor/patient; we link back via back_populates)
    doctor_invoices = db.relationship(
        "Invoice",
        foreign_keys="Invoice.doctor_id",
        back_populates="doctor",
        lazy=True,
    )

    patient_invoices = db.relationship(
        "Invoice",
        foreign_keys="Invoice.patient_id",
        back_populates="patient",
        lazy=True,
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __init__(self, name, email, user_type, password=None):
        self.name = name
        self.email = email
        self.user_type = user_type
        if password:
            self.password_hash = generate_password_hash(password)
        else:
            self.password_hash = ""

        # Create XRPL account when user is created
        wallet = create_account()
        self.xrp_address = wallet.address
        self.xrp_seed = wallet.seed