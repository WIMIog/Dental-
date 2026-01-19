# routes/__init__.py
def register_routes(app):
    from .auth import auth_bp
    from .patient import patient_bp
    from .doctor import doctor_bp
    from .admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(admin_bp)
