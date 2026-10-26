from flask import Flask, jsonify
from flask_login import LoginManager
from config import Config
from database import db

login_manager = LoginManager()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    from models import (
        User,
        Student,
        Subject,
        AttendanceSession,
        AttendanceRecord,
        SyllabusTopic
    )

    from auth_routes import auth_bp
    from attendance_routes import attendance_bp
    from syllabus_routes import syllabus_bp
    from report_routes import report_bp

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(User, int(user_id))
        except (TypeError, ValueError):
            return None

    app.register_blueprint(auth_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(syllabus_bp)
    app.register_blueprint(report_bp)

    with app.app_context():
        db.create_all()

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)