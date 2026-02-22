from extensions import db
from datetime import datetime

class Invoice(db.Model):
    __tablename__ = "invoice"

    id = db.Column(db.Integer, primary_key=True)

    doctor_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    # relationships
    doctor = db.relationship("User", foreign_keys=[doctor_id], back_populates="doctor_invoices")
    patient = db.relationship("User", foreign_keys=[patient_id], back_populates="patient_invoices")

    amount = db.Column(db.Float, nullable=False)

    treatment_description = db.Column(db.String(500), nullable=True)

    crowdfund_enabled = db.Column(db.Boolean, default=False)

    status = db.Column(db.String(50), default="unpaid")  # unpaid, partially_paid, paid, reported, redacted

    payments = db.Column(db.JSON, default=list)

    # Crawlback: report suspicious / fraudulent charge
    reported_at = db.Column(db.DateTime, nullable=True)
    report_reason = db.Column(db.String(500), nullable=True)
    reported_by_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    redacted_at = db.Column(db.DateTime, nullable=True)
    redacted_by_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def add_payment(self, payer_id, amount, tx_hash, method):
        payment = {
            "payer_id": payer_id,
            "amount": amount,
            "tx_hash": tx_hash,
            "method": method
        }

        if not self.payments:
            self.payments = []

        self.payments.append(payment)

        total_paid = sum(p["amount"] for p in self.payments)

        if total_paid >= self.amount:
            self.status = "paid"
        else:
            self.status = "partially_paid"