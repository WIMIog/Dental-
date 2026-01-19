# routes/doctor.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import Appointment, db

doctor_bp = Blueprint('doctor', __name__, url_prefix='/doctor')

# ---------------- DOCTOR DASHBOARD ----------------
@doctor_bp.route("/")
@login_required
def doctor_dashboard():
    if current_user.role != 'doctor':
        flash("Access denied: Doctors only", "danger")
        return redirect(url_for('auth.home'))

    # Appointments assigned to this doctor
    my_appointments = Appointment.query.filter_by(doctor_id=current_user.id).all()

    # Unassigned appointments
    unassigned_appointments = Appointment.query.filter_by(doctor_id=None).all()

    return render_template(
        "doctor/dashboard.html",
        my_appointments=my_appointments,
        unassigned_appointments=unassigned_appointments
    )


# ---------------- UPDATE APPOINTMENT STATUS ----------------
@doctor_bp.route("/appointments/update_status/<int:appt_id>", methods=['POST'])
@login_required
def update_appt_status(appt_id):
    if current_user.role != 'doctor':
        flash("Access denied", "danger")
        return redirect(url_for('auth.home'))

    appt = Appointment.query.get_or_404(appt_id)

    # Only allow doctor to update their own appointments
    if appt.doctor_id != current_user.id:
        flash("You cannot modify this appointment", "danger")
        return redirect(url_for('doctor.doctor_dashboard'))

    status = request.form.get('status')
    if status not in ['approved', 'rejected']:
        flash("Invalid status", "danger")
        return redirect(url_for('doctor.doctor_dashboard'))

    appt.status = status
    db.session.commit()
    flash(f"Appointment {status} successfully!", "success")
    return redirect(url_for('doctor.doctor_dashboard'))


# ---------------- OPTIONAL: VIEW SINGLE APPOINTMENT ----------------
@doctor_bp.route("/appointments/<int:appt_id>")
@login_required
def view_appointment(appt_id):
    if current_user.role != 'doctor':
        flash("Access denied", "danger")
        return redirect(url_for('auth.home'))

    appt = Appointment.query.get_or_404(appt_id)
    if appt.doctor_id != current_user.id:
        flash("You cannot view this appointment", "danger")
        return redirect(url_for('doctor.doctor_dashboard'))

    return render_template("doctor/view_appointment.html", appointment=appt)
