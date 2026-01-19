# routes/admin.py
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from models import User, Appointment, SiteSettings, db, HomeContent
from werkzeug.utils import secure_filename
import os
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Decorator to restrict to admin only
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash("Access denied!", "danger")
            return redirect(url_for('auth.home'))
        return f(*args, **kwargs)
    return decorated_function

# ---------------- DASHBOARD -----------------
@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()
    total_appointments = Appointment.query.count()
    pending = Appointment.query.filter_by(status="pending").count()
    approved = Appointment.query.filter_by(status="approved").count()
    rejected = Appointment.query.filter_by(status="rejected").count()
    return render_template(
        "admin/dashboard.html",
        users=total_users,
        appointments=total_appointments,
        pending=pending,
        approved=approved,
        rejected=rejected
    )

# ---------------- USERS -----------------
@admin_bp.route("/users")
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template("admin/users.html", users=users)

@admin_bp.route("/users/update/<int:user_id>", methods=['POST'])
@login_required
@admin_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    if new_role not in ['patient', 'doctor', 'admin']:
        flash("Invalid role", "danger")
        return redirect(url_for('admin.users'))
    user.role = new_role
    db.session.commit()
    flash(f"{user.name} role updated to {new_role}", "success")
    return redirect(url_for('admin.users'))

@admin_bp.route("/users/delete/<int:user_id>", methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f"User {user.name} deleted", "success")
    return redirect(url_for('admin.users'))

# ---------------- APPOINTMENTS -----------------
@admin_bp.route("/appointments")
@login_required
@admin_required
def appointments():
    appointments = Appointment.query.all()
    return render_template("admin/appointments.html", appointments=appointments)

@admin_bp.route('/appointments/update_status/<int:appt_id>', methods=['POST'])
@login_required
@admin_required
def update_appt_status(appt_id):
    status = request.form.get('status')
    appt = Appointment.query.get_or_404(appt_id)
    if status not in ['approved', 'rejected']:
        flash("Invalid status", "danger")
        return redirect(url_for('admin.appointments'))
    appt.status = status
    db.session.commit()
    flash(f"Appointment {status} successfully!", "success")
    return redirect(url_for('admin.appointments'))

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_bp.route('/home-content/edit/<int:content_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_home_content(content_id):
    content = HomeContent.query.get_or_404(content_id)

    if request.method == 'POST':
        # Update text fields
        content.section_type = request.form['section_type']
        content.title = request.form['title']
        content.description = request.form['description']
        content.order = int(request.form['order'])

        # Handle optional image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_path = os.path.join(current_app.root_path, 'static/uploads', filename)
                file.save(upload_path)
                content.image = filename

        try:
            db.session.commit()
            flash('Homepage content updated successfully!', 'success')
            return redirect(url_for('admin.home_content_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating content: {str(e)}', 'danger')
            return redirect(request.url)

    return render_template('admin/edit_home_content.html', content=content)



# ---------------- SITE SETTINGS -----------------
@admin_bp.route("/settings", methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    settings = SiteSettings.query.first()
    if not settings:
        settings = SiteSettings(clinic_name="My Clinic", working_hours="9AM - 5PM")
        db.session.add(settings)
        db.session.commit()

    if request.method == 'POST':
        settings.clinic_name = request.form['clinic_name']
        settings.working_hours = request.form['working_hours']
        db.session.commit()
        flash("Settings updated successfully!", "success")
        return redirect(url_for('admin.settings'))

    return render_template("admin/settings.html", settings=settings)

# ---------------- HOME CONTENT (DYNAMIC) -----------------
@admin_bp.route('/home-content')
@login_required
@admin_required
def home_content_list():
    contents = HomeContent.query.order_by(HomeContent.order).all()
    return render_template('admin/home_content_list.html', contents=contents)

@admin_bp.route('/home-content/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_home_content():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        section_type = request.form['section_type']
        order = int(request.form.get('order', 0))

        image_file = request.files.get('image')
        filename = None
        if image_file:
            filename = secure_filename(image_file.filename)
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
            os.makedirs(upload_folder, exist_ok=True)
            image_file.save(os.path.join(upload_folder, filename))

        new_content = HomeContent(
            title=title,
            description=description,
            section_type=section_type,
            image=filename,
            order=order
        )
        db.session.add(new_content)
        db.session.commit()
        flash('Content added successfully!', 'success')
        return redirect(url_for('admin.home_content_list'))

    return render_template('admin/add_home_content.html')

@admin_bp.route('/home-content/delete/<int:content_id>', methods=['POST'])
@login_required
@admin_required
def delete_home_content(content_id):
    content = HomeContent.query.get_or_404(content_id)
    # Delete image file if exists
    if content.image:
        try:
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], content.image))
        except Exception:
            pass
    db.session.delete(content)
    db.session.commit()
    flash("Content deleted successfully!", "success")
    return redirect(url_for('admin.home_content_list'))
