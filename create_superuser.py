# create_superuser.py
from getpass import getpass
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def create_superuser():
    print("=== Create a Superuser ===")
    name = input("Full Name: ").strip()
    email = input("Email: ").strip()

    # Ensure password input is hidden
    while True:
        password = getpass("Password: ")
        password_confirm = getpass("Confirm Password: ")
        if password != password_confirm:
            print("Passwords do not match. Try again.")
        elif len(password) < 6:
            print("Password too short, minimum 6 characters.")
        else:
            break

    with app.app_context():
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            print(f"User with email '{email}' already exists!")
            return

        admin = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            role="admin"
        )
        db.session.add(admin)
        db.session.commit()
        print(f"Superuser '{name}' created successfully!")

if __name__ == "__main__":
    create_superuser()
