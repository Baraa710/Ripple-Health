from extensions import db
from datetime import datetime

class Invoice(db.Model):
    __tablename__ = "invoice"

    id = db.Column(db.Integer, primary_key=True)

    doctor_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    amount = db.Column(db.Float, nullable=False)

    crowdfund_enabled = db.Column(db.Boolean, default=False)

    status = db.Column(db.String(50), default="unpaid")  
    # unpaid, partially_paid, paid

    payments = db.Column(db.JSON, default=list)
    # list of dicts:
    # {payer_id, amount, tx_hash, method}

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def add_payment(self, payer_id, amount, tx_hash, method):
        payment = {
            "payer_id": payer_id,
            "amount": amount,
            "tx_hash": tx_hash,
            "method": method
        }

        # Ensure payments list exists
        if not self.payments:
            self.payments = []

        self.payments.append(payment)

        total_paid = sum(p["amount"] for p in self.payments)

        if total_paid >= self.amount:
            self.status = "paid"
        else:
            self.status = "partially_paid"