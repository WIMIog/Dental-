from flask import Flask
from flask_login import LoginManager
import os
from models import db, User
from routes import register_routes

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'dentist.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Upload folder for admin-managed images
UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # optional: limit 2MB

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register all route blueprints
register_routes(app)

# =========================
# Start the Flask server
# =========================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # creates tables if they don't exist
    app.run(debug=True)
