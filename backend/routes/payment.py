from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models.invoice import Invoice
from models.campaign import Campaign
from extensions import db
from sqlalchemy.orm.attributes import flag_modified
from xrpl_utils.xrpl_utils import send_payment  

payment_bp = Blueprint("payment", __name__)


@payment_bp.route("/pay/<int:invoice_id>", methods=["POST"])
@login_required
def pay_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    if invoice.status in ("reported", "redacted"):
        return jsonify({"error": "Cannot pay reported or redacted invoice"}), 400

    data = request.get_json() or request.form
    amount_raw = data.get("amount")
    if amount_raw is None:
        return jsonify({"error": "amount required"}), 400
    try:
        amount = float(amount_raw)
    except (TypeError, ValueError):
        return jsonify({"error": "invalid amount"}), 400
    if amount <= 0:
        return jsonify({"error": "amount must be positive"}), 400
    method = data.get("method", "direct")  # direct or crowdfunding


    # If crowdfunding is disabled, only patient can pay
    if not invoice.crowdfund_enabled and current_user.id != invoice.patient_id:
        return jsonify({"error": "Crowdfunding disabled"}), 403

    # Determine recipient (doctor gets paid)
    recipient_address = invoice.doctor.xrp_address

    # Send XRP using XRPL
    tx_hash = send_payment(
        sender_seed=current_user.xrp_seed,
        recipient_address=recipient_address,
        amount=str(amount)
    )

    if not tx_hash:
        return jsonify({"error": "Blockchain payment failed"}), 400

    # Save payment in database
    invoice.add_payment(
        payer_id=current_user.id,
        amount=amount,
        tx_hash=tx_hash,
        method=method
    )

    flag_modified(invoice, "payments")
    campaign = Campaign.query.filter_by(invoice_id=invoice.id).first()
    if campaign:
        campaign.current_amount = sum(p["amount"] for p in invoice.payments)
        if campaign.current_amount >= campaign.target_amount:
            campaign.status = "completed"
    db.session.commit()

    return jsonify({
        "message": "Payment successful",
        "tx_hash": tx_hash,
        "status": invoice.status,
    })