# routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from models import User, db, HomeContent
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

# ---------------- HOME -----------------
@auth_bp.route('/')
def home():
    contents = HomeContent.query.order_by(HomeContent.order).all()
    return render_template('home.html', home_contents=contents)

# ---------------- REGISTER -----------------
@auth_bp.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        role = request.form.get('role', 'patient')

        if User.query.filter_by(email=email).first():
            flash("Email already exists", "danger")
            return redirect(url_for('auth.register'))

        new_user = User(name=name, email=email, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created! Please log in.", "success")
        return redirect(url_for('auth.login'))
    return render_template("register.html")

# ---------------- LOGIN -----------------
@auth_bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Logged in successfully", "success")
            return redirect(url_for('auth.home'))
        else:
            flash("Invalid credentials", "danger")
            return redirect(url_for('auth.login'))

    return render_template("login.html")

# ---------------- LOGOUT -----------------
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully", "success")
    return redirect(url_for('auth.home'))
