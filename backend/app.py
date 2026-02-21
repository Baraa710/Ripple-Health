from flask import Flask
from extensions import init_db, close_db
from routes.users import users_bp
# Add other blueprints as needed

app = Flask(__name__)

app.teardown_appcontext(close_db)

with app.app_context():
    init_db()

app.register_blueprint(users_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)