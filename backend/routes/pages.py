from flask import Blueprint, render_template
from flask_login import current_user

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/")
def home():
    return render_template("base.html")


@pages_bp.route("/patients/login")
def patient_login():
    return render_template("patients/login.html")


@pages_bp.route("/patients/signup")
def patient_signup():
    return render_template("patients/signup.html")


@pages_bp.route("/patients/dashboard")
def patient_dashboard():
    return render_template("patients/dashboard.html")


@pages_bp.route("/doctors/login")
def doctor_login():
    return render_template("doctors/login.html")


@pages_bp.route("/doctors/signup")
def doctor_signup():
    return render_template("doctors/signup.html")


@pages_bp.route("/doctors/dashboard")
def doctor_dashboard():
    return render_template("doctors/dashboard.html")


@pages_bp.route("/donors/login")
def donor_login():
    return render_template("donors/login.html")


@pages_bp.route("/donors/signup")
def donor_signup():
    return render_template("donors/signup.html")


@pages_bp.route("/donors/dashboard")
def donor_dashboard():
    return render_template("donors/dashboard.html")


@pages_bp.route("/campaigns")
def campaigns():
    return render_template("campaigns.html")
