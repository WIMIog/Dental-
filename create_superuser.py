# create_superuser.py
import os
from getpass import getpass
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def create_superuser():
    if os.getenv("FLASK_ENV") == "production":
        print("❌ Superuser creation disabled in production")
        return

    print("=== Create a Superuser ===")
    name = input("Full Name: ").strip()
    email = input("Email: ").strip()

    while True:
        password = getpass("Password: ")
        password_confirm = getpass("Confirm Password: ")
        if password != password_confirm:
            print("Passwords do not match. Try again.")
        elif len(password) < 6:
            print("Password too short (min 6 chars).")
        else:
            break

    with app.app_context():
        if User.query.filter_by(email=email).first():
            print(f"❌ User with email '{email}' already exists!")
            return

        superadmin = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            role="superadmin",
       
        )

        db.session.add(superadmin)
        db.session.commit()
        print(f"✅ Superuser '{name}' created successfully!")

if __name__ == "__main__":
    create_superuser()
