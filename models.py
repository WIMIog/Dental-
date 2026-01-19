# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='patient')


# models.py
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time)
    status = db.Column(db.String(20), default='pending')

    # New professional fields
    message = db.Column(db.String(255))          # optional message
    patient_full_name = db.Column(db.String(100))
    patient_insurance = db.Column(db.String(100))

    patient = db.relationship('User', foreign_keys=[patient_id])
    doctor = db.relationship('User', foreign_keys=[doctor_id])



class SiteSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clinic_name = db.Column(db.String(100))
    working_hours = db.Column(db.String(100))

class HomeContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    section_type = db.Column(db.String(50))  # e.g., "hero", "service", "testimonial", "logo"
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    image = db.Column(db.String(200))  # store filename of uploaded image
    order = db.Column(db.Integer, default=0)  # for sorting cards
    created_at = db.Column(db.DateTime, default=datetime.utcnow)