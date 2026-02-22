from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    """Bind DB to app and create tables."""
    db.init_app(app)
    with app.app_context():
        db.create_all()


def close_db(exception=None):
    """Teardown: remove session."""
    try:
        db.session.remove()
    except Exception:
        pass