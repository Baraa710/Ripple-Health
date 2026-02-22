from flask import Blueprint, request, jsonify, current_app
from models.campaign import Campaign
from models.user import User
from models.invoice import Invoice
from xrpl_utils.xrpl_utils import check_credential

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
        on_chain = False
        issuer_seed = current_app.config.get("ISSUER_SEED", "")
        if issuer_seed and doc:
            from xrpl.wallet import Wallet
            issuer_address = Wallet.from_seed(issuer_seed).address
            on_chain = check_credential(doc.xrp_address, issuer_address)
        out.append({
            **c.to_dict(),
            "doctor_name": doc.name if doc else None,
            "is_verified_doctor": doc.is_verified_doctor if doc else False,
            "on_chain_verified": on_chain,
        })
    return jsonify({"campaigns": out}), 200


@campaign_bp.route("/<int:campaign_id>", methods=["GET"])
def get_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    doc = User.query.get(campaign.doctor_id)
    inv = Invoice.query.get(campaign.invoice_id)
    on_chain = False
    issuer_seed = current_app.config.get("ISSUER_SEED", "")
    if issuer_seed and doc:
        from xrpl.wallet import Wallet
        issuer_address = Wallet.from_seed(issuer_seed).address
        on_chain = check_credential(doc.xrp_address, issuer_address)
    return jsonify({
        **campaign.to_dict(),
        "doctor_name": doc.name if doc else None,
        "is_verified_doctor": doc.is_verified_doctor if doc else False,
        "on_chain_verified": on_chain,
        "invoice_amount": inv.amount if inv else None,
        "invoice_status": inv.status if inv else None,
    }), 200
