from extensions import db
from datetime import datetime


class ReserveAccount(db.Model):
    """Doctor reserve (liquidity pool) for covering crowdfunding gaps."""
    __tablename__ = "reserve_account"

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True)

    balance = db.Column(db.Float, default=0.0, nullable=False)  # in XRP
    currency = db.Column(db.String(10), default="XRP")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    doctor = db.relationship("User", backref=db.backref("reserve_account", uselist=False))
