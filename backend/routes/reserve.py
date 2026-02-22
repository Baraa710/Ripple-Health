from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models.invoice import Invoice
from models.reserve import ReserveAccount
from models.user import User
from extensions import db

reserve_bp = Blueprint("reserve", __name__)


def _get_or_create_reserve(doctor_id):
    acc = ReserveAccount.query.filter_by(doctor_id=doctor_id).first()
    if not acc:
        acc = ReserveAccount(doctor_id=doctor_id)
        db.session.add(acc)
        db.session.commit()
    return acc


@reserve_bp.route("/balance", methods=["GET"])
@login_required
def get_balance():
    if current_user.user_type != "doctor":
        return jsonify({"error": "Only doctors have reserve accounts"}), 403
    acc = _get_or_create_reserve(current_user.id)
    return jsonify({"doctor_id": current_user.id, "balance": acc.balance, "currency": acc.currency}), 200


@reserve_bp.route("/add", methods=["POST"])
@login_required
def add_to_reserve():
    if current_user.user_type != "doctor":
        return jsonify({"error": "Only doctors can add to their reserve"}), 403
    data = request.get_json() or request.form
    amount = data.get("amount")
    if amount is None:
        return jsonify({"error": "amount required"}), 400
    amount = float(amount)
    if amount <= 0:
        return jsonify({"error": "amount must be positive"}), 400
    acc = _get_or_create_reserve(current_user.id)
    acc.balance += amount
    db.session.commit()
    return jsonify({"message": "Added to reserve", "balance": acc.balance}), 200


@reserve_bp.route("/use-for-invoice/<int:invoice_id>", methods=["POST"])
@login_required
def use_reserve_for_invoice(invoice_id):
    """Use reserve to cover the gap for a partially-paid invoice (doctor gets full amount)."""
    if current_user.user_type != "doctor":
        return jsonify({"error": "Only doctors can use reserve for invoices"}), 403

    invoice = Invoice.query.get_or_404(invoice_id)
    if invoice.doctor_id != current_user.id:
        return jsonify({"error": "Invoice does not belong to you"}), 403
    if invoice.status == "paid":
        return jsonify({"error": "Invoice is already paid"}), 400

    total_paid = sum(p["amount"] for p in (invoice.payments or []))
    gap = invoice.amount - total_paid
    if gap <= 0:
        return jsonify({"error": "No gap to cover"}), 400

    acc = _get_or_create_reserve(current_user.id)
    if acc.balance < gap:
        return jsonify({"error": "Insufficient reserve balance", "balance": acc.balance, "gap": gap}), 400

    acc.balance -= gap
    invoice.status = "paid"
    if not invoice.payments:
        invoice.payments = []
    invoice.payments.append({
        "payer_id": None,
        "amount": gap,
        "tx_hash": None,
        "method": "reserve",
    })
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(invoice, "payments")
    db.session.commit()

    return jsonify({
        "message": "Reserve applied; invoice paid",
        "invoice_id": invoice_id,
        "gap_covered": gap,
        "reserve_balance": acc.balance,
    }), 200
