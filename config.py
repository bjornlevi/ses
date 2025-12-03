import os


class Config:
    _raw_prefix = os.environ.get("APP_URL_PREFIX", "").strip()
    if _raw_prefix and not _raw_prefix.startswith("/"):
        _raw_prefix = f"/{_raw_prefix}"

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(os.getcwd(), 'app.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "localhost")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 25))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "false").lower() == "true"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "noreply@example.com")
    SECURITY_EMAIL_SENDER = MAIL_DEFAULT_SENDER
    APP_NAME = os.environ.get("APP_NAME", "Debate Hub")
    APP_URL_PREFIX = _raw_prefix.rstrip("/")
    WTF_CSRF_TIME_LIMIT = None
