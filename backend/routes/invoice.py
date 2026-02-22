from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models.invoice import Invoice
from models.user import User
from models.campaign import Campaign
from extensions import db

invoice_bp = Blueprint("invoice", __name__)


@invoice_bp.route("/create", methods=["POST"])
@login_required
def create_invoice():
    if current_user.user_type != "doctor":
        return jsonify({"error": "Only doctors can create invoices"}), 403

    data = request.get_json() or request.form
    patient_id = data.get("patient_id")
    amount = data.get("amount")
    crowdfund_enabled = data.get("crowdfund_enabled", data.get("crowdfund", False))
    if isinstance(crowdfund_enabled, str):
        crowdfund_enabled = crowdfund_enabled.lower() in ("true", "1", "yes")

    if not patient_id or amount is None:
        return jsonify({"error": "patient_id and amount required"}), 400

    patient = User.query.get(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    if patient.user_type != "patient":
        return jsonify({"error": "Target user is not a patient"}), 400

    treatment_description = (data.get("treatment_description") or "").strip() or None
    invoice = Invoice(
        doctor_id=current_user.id,
        patient_id=int(patient_id),
        amount=float(amount),
        treatment_description=treatment_description[:500] if treatment_description else None,
        crowdfund_enabled=bool(crowdfund_enabled),
    )
    db.session.add(invoice)
    db.session.flush()

    if crowdfund_enabled:
        campaign = Campaign(
            invoice_id=invoice.id,
            doctor_id=current_user.id,
            name=f"Campaign for invoice #{invoice.id}",
            description="Medical crowdfunding",
            target_amount=float(amount),
        )
        db.session.add(campaign)

    db.session.commit()

    return jsonify({"message": "Invoice created", "invoice_id": invoice.id}), 
def _invoice_json(invoice):
    return {
        "id": invoice.id,
        "doctor_id": invoice.doctor_id,
        "patient_id": invoice.patient_id,
        "amount": invoice.amount,
        "treatment_description": invoice.treatment_description,
        "status": invoice.status,
        "crowdfund_enabled": invoice.crowdfund_enabled,
        "payments": invoice.payments or [],
        "reported_at": invoice.reported_at.isoformat() if invoice.reported_at else None,
        "report_reason": invoice.report_reason,
        "redacted_at": invoice.redacted_at.isoformat() if invoice.redacted_at else None,
    }


@invoice_bp.route("/<int:invoice_id>", methods=["GET"])
@login_required
def view_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    return jsonify(_invoice_json(invoice))


@invoice_bp.route("/<int:invoice_id>", methods=["PATCH"])
@login_required
def update_invoice_crowdfund(invoice_id):
    """Patient can enable or disable crowdfunding for their own invoice."""
    invoice = Invoice.query.get_or_404(invoice_id)
    if current_user.id != invoice.patient_id:
        return jsonify({"error": "Only the patient on this invoice can update crowdfunding"}), 403
    if invoice.status in ("paid", "redacted", "reported"):
        return jsonify({"error": "Cannot change crowdfunding on a paid, redacted, or reported invoice"}), 400

    data = request.get_json() or request.form
    if not data or ("crowdfund_enabled" not in data and "crowdfund" not in data):
        return jsonify(_invoice_json(invoice)), 200

    crowdfund_enabled = data.get("crowdfund_enabled", data.get("crowdfund"))
    if isinstance(crowdfund_enabled, str):
        crowdfund_enabled = crowdfund_enabled.lower() in ("true", "1", "yes")
    else:
        crowdfund_enabled = bool(crowdfund_enabled)

    invoice.crowdfund_enabled = crowdfund_enabled

    if crowdfund_enabled:
        campaign = Campaign.query.filter_by(invoice_id=invoice.id).first()
        if not campaign:
            campaign = Campaign(
                invoice_id=invoice.id,
                doctor_id=invoice.doctor_id,
                name=f"Campaign for invoice #{invoice.id}",
                description="Medical crowdfunding",
                target_amount=invoice.amount,
            )
            db.session.add(campaign)
    else:
        campaign = Campaign.query.filter_by(invoice_id=invoice.id).first()
        if campaign:
            campaign.status = "cancelled"

    db.session.commit()
    return jsonify(_invoice_json(invoice)), 200


@invoice_bp.route("/<int:invoice_id>/report", methods=["POST"])
@login_required
def report_invoice(invoice_id):
    """Report a suspicious or fraudulent charge (crawlback)."""
    invoice = Invoice.query.get_or_404(invoice_id)
    if invoice.status == "redacted":
        return jsonify({"error": "Invoice already redacted"}), 400

    data = request.get_json() or request.form
    reason = data.get("reason", "").strip() or "Suspicious or fraudulent charge"
    invoice.status = "reported"
    invoice.reported_at = datetime.utcnow()
    invoice.report_reason = reason[:500]
    invoice.reported_by_id = current_user.id
    db.session.commit()
    return jsonify({"message": "Invoice reported", "invoice_id": invoice_id}), 200


@invoice_bp.route("/<int:invoice_id>/redact", methods=["POST"])
@login_required
def redact_invoice(invoice_id):
    """Redact an invoice (reverse/fraud outcome). Only admin."""
    import os
    admin_email = os.environ.get("ADMIN_EMAIL")
    if not admin_email or current_user.email != admin_email:
        return jsonify({"error": "Only admin can redact invoices"}), 403

    invoice = Invoice.query.get_or_404(invoice_id)
    invoice.status = "redacted"
    invoice.redacted_at = datetime.utcnow()
    invoice.redacted_by_id = current_user.id
    db.session.commit()
    return jsonify({"message": "Invoice redacted", "invoice_id": invoice_id}), 200