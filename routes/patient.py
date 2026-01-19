# routes/patient.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Appointment, db
from datetime import datetime, date, time


patient_bp = Blueprint('patient', __name__)

# routes/patient.py
@patient_bp.route("/book", methods=['GET', 'POST'])
@login_required
def book():
    if request.method == 'POST':
        date_str = request.form['date']        # e.g. '2026-01-10'
        time_str = request.form['time']        # e.g. '14:44'
        message = request.form.get('message')
        full_name = request.form.get('full_name')
        insurance = request.form.get('insurance')

        # Convert to Python objects
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date format. Use YYYY-MM-DD.")
            return redirect(url_for('patient.book'))

        try:
            time_obj = datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            flash("Invalid time format. Use HH:MM (24-hour).")
            return redirect(url_for('patient.book'))

        new_appointment = Appointment(
            patient_id=current_user.id,
            date=date_obj,
            time=time_obj,
            message=message,
            patient_full_name=full_name,
            patient_insurance=insurance
        )

        db.session.add(new_appointment)
        db.session.commit()
        flash("Appointment requested successfully!")
        return redirect(url_for('patient.book'))

    return render_template("book.html")



@patient_bp.route("/my-appointments")
@login_required
def my_appointments():
    appointments = Appointment.query.filter_by(patient_id=current_user.id).all()
    return render_template("appointments.html", appointments=appointments)
