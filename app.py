# app.py

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

from models import db, User
from routes import register_routes

# ----------------------
# Load environment variables
# ----------------------
load_dotenv()  # Loads variables from .env

USE_SUPABASE = os.getenv("USE_SUPABASE", "False").lower() in ["true", "1", "yes"]
SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

# ----------------------
# Flask App Setup
# ----------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ----------------------
# Database Configuration
# ----------------------
basedir = os.path.abspath(os.path.dirname(__file__))

if USE_SUPABASE:
    if not SUPABASE_DB_URL:
        raise ValueError("SUPABASE_DB_URL must be set when USE_SUPABASE=True")

    app.config["SQLALCHEMY_DATABASE_URI"] = SUPABASE_DB_URL

    # 🔑 VERY IMPORTANT: Supabase connection stability
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,   # Fixes 'server closed the connection unexpectedly'
        "pool_recycle": 300,     # Recycle connections every 5 minutes
        "pool_size": 5,
        "max_overflow": 10,
    }

    print("Using Supabase/Postgres DB")

else:
    # Local SQLite (development only)
    instance_folder = os.path.join(basedir, "instance")
    os.makedirs(instance_folder, exist_ok=True)

    db_path = os.path.join(instance_folder, "dentist.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

    print("Using local SQLite DB:", db_path)

# ----------------------
# Initialize Database
# ----------------------
db.init_app(app)

# ----------------------
# Flask-Migrate Setup
# ----------------------
migrate = Migrate(app, db)

# ----------------------
# Upload Folder Setup
# ----------------------
UPLOAD_FOLDER = os.path.join(basedir, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2MB max upload

# ----------------------
# Login Manager Setup
# ----------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ----------------------
# Register Blueprints
# ----------------------
register_routes(app)

# ----------------------
# Initialize SQLite DB (ONLY for local use)
# ----------------------
if not USE_SUPABASE:
    with app.app_context():
        db.create_all()

# ----------------------
# Run Server
# ----------------------
if __name__ == "__main__":
    app.run(debug=True)
