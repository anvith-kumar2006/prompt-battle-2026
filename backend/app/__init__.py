from flask import Flask
from backend.config import Config
from backend.app.extensions import db, login_manager, limiter, mail
import threading

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
    mail.init_app(app)
    
    # Login manager config
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # User loader
    @login_manager.user_loader
    def load_user(user_id):
        from backend.app.models import User
        return User.query.get(int(user_id))

    # Register blueprints
    from backend.app.api import auth, students, providers, rides, consent, trips, gps, incidents, notifications, admin_bp, health
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(students.bp)
    app.register_blueprint(providers.bp)
    app.register_blueprint(rides.bp)
    app.register_blueprint(consent.bp)
    app.register_blueprint(trips.bp)
    app.register_blueprint(gps.bp)
    app.register_blueprint(incidents.bp)
    app.register_blueprint(notifications.bp)
    app.register_blueprint(admin_bp.bp)
    app.register_blueprint(health.bp)
    
    # Register template routes
    from backend.app import routes
    routes.register_routes(app)
    
    # Error handlers
    from backend.app import errors
    errors.register_error_handlers(app)
    
    # Start background worker (disabled until notify service is implemented)
    # if not app.config.get('TESTING'):
    #     from backend.app.services.notify import start_email_worker
    #     worker_thread = threading.Thread(target=start_email_worker, args=(app,), daemon=True)
    #     worker_thread.start()
    
    return app
