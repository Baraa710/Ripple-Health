from extensions import db
from datetime import datetime


class Campaign(db.Model):
    """Crowdfunding campaign linked to an invoice (one-to-one when crowdfund_enabled)."""
    __tablename__ = "campaign"

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey("invoice.id"), nullable=False, unique=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(1000), default="")

    target_amount = db.Column(db.Float, nullable=False)  # XRP, matches invoice.amount
    current_amount = db.Column(db.Float, default=0.0)

    status = db.Column(db.String(50), default="active")  # active, completed, cancelled

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)

    invoice = db.relationship("Invoice", backref=db.backref("campaign", uselist=False))
    doctor = db.relationship("User", backref="campaigns")

    def to_dict(self):
        return {
            "id": self.id,
            "invoice_id": self.invoice_id,
            "doctor_id": self.doctor_id,
            "name": self.name,
            "description": self.description,
            "target_amount": self.target_amount,
            "current_amount": self.current_amount,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
        }
