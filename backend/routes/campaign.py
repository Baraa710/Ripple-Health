from flask import Blueprint, request, jsonify
from models.campaign import Campaign
from models.user import User
from models.invoice import Invoice

campaign_bp = Blueprint("campaign", __name__)


@campaign_bp.route("", methods=["GET"])
def list_campaigns():
    """List active crowdfunding campaigns (public). Optionally filter by verified doctor."""
    verified_only = request.args.get("verified_only", "").lower() in ("true", "1", "yes")
    campaigns = Campaign.query.filter(Campaign.status == "active").all()

    out = []
    for c in campaigns:
        if verified_only:
            doc = User.query.get(c.doctor_id)
            if not doc or not doc.is_verified_doctor:
                continue
        inv = Invoice.query.get(c.invoice_id)
        if inv and inv.status in ("reported", "redacted"):
            continue
        doc = User.query.get(c.doctor_id)
        out.append({
            **c.to_dict(),
            "doctor_name": doc.name if doc else None,
            "is_verified_doctor": doc.is_verified_doctor if doc else False,
        })
    return jsonify({"campaigns": out}), 200


@campaign_bp.route("/<int:campaign_id>", methods=["GET"])
def get_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    doc = User.query.get(campaign.doctor_id)
    inv = Invoice.query.get(campaign.invoice_id)
    return jsonify({
        **campaign.to_dict(),
        "doctor_name": doc.name if doc else None,
        "is_verified_doctor": doc.is_verified_doctor if doc else False,
        "invoice_amount": inv.amount if inv else None,
        "invoice_status": inv.status if inv else None,
    }), 200
