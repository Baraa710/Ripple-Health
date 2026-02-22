import os
from flask import Flask
from flask_login import LoginManager
from extensions import init_db, close_db, db
from routes.users import users_bp
from routes.invoice import invoice_bp
from routes.payment import payment_bp
from routes.reserve import reserve_bp
from routes.campaign import campaign_bp
from routes.pages import pages_bp
from models.user import User
from models.invoice import Invoice
from models.reserve import ReserveAccount
from models.campaign import Campaign

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "..", "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "..", "static"),
)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
_db_dir = os.path.dirname(os.path.abspath(__file__))
_db_path = os.path.normpath(os.path.join(_db_dir, "ripple_health.db")).replace("\\", "/")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URI", f"sqlite:///{_db_path}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["ISSUER_SEED"] = os.environ.get("ISSUER_SEED", "")

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
    from flask import jsonify
    return jsonify({"error": "Login required"}), 401

app.teardown_appcontext(close_db)
init_db(app)

app.register_blueprint(users_bp, url_prefix="/api")
app.register_blueprint(invoice_bp, url_prefix="/api/invoices")
app.register_blueprint(payment_bp, url_prefix="/api/payments")
app.register_blueprint(reserve_bp, url_prefix="/api/reserve")
app.register_blueprint(campaign_bp, url_prefix="/api/campaigns")
app.register_blueprint(pages_bp)


def _print_routes():
    """Print registered routes at startup (helpful for debugging 404s)."""
    for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
        if "static" not in rule.rule:
            print(f"  {rule.rule}")


if __name__ == "__main__":
    print("Registered routes:")
    _print_routes()
    if app.config.get("ISSUER_SEED"):
        from xrpl.wallet import Wallet
        print(f"  ISSUER_SEED is set (issuer address: {Wallet.from_seed(app.config['ISSUER_SEED']).address})")
    else:
        print("  WARNING: ISSUER_SEED not set — on-chain credentials disabled")
    app.run(debug=True)