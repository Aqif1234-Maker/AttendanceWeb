from flask import Flask, session, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

from config import config


db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()


def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config['default']))

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'auth.teacher_login'

    from .models import Teacher, StudentAccount

    @login_manager.user_loader
    def load_user(user_id):
        user_type = session.get('user_type')
        if user_type == 'teacher':
            return Teacher.query.get(int(user_id))
        if user_type == 'student':
            return StudentAccount.query.get(int(user_id))
        return None

    @login_manager.unauthorized_handler
    def unauthorized():
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Unauthorized'}), 401
        return redirect(url_for('auth.landing'))

    from .routes.auth import auth_bp
    from .routes.teacher import teacher_bp
    from .routes.student import student_bp
    from .routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(api_bp)

    @app.context_processor
    def inject_pending_count():
        pending_count = 0
        if session.get('user_type') == 'teacher':
            pending_count = StudentAccount.query.filter_by(approved=False).count()
        return dict(pending_approvals=pending_count)

    return app
