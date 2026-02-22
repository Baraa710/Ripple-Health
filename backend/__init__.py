from flask import Flask
from extensions import db

app = Flask(__name__)
db.init_app(app)