from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from dotenv import load_dotenv

load_dotenv()
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()


def create_app(config_class: type[Config] = Config) -> Flask:
    prefix = config_class.APP_URL_PREFIX
    if prefix and not prefix.startswith("/"):
        prefix = f"/{prefix}"
    static_path = f"{prefix}/static" if prefix else "/static"

    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates",
        static_url_path=static_path,
    )
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    from app.auth import auth_bp
    from app.routes import main_bp

    app.register_blueprint(auth_bp, url_prefix=prefix or None)
    app.register_blueprint(main_bp, url_prefix=prefix or None)

    return app
