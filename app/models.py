from datetime import datetime
from enum import Enum

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import current_app

from app import db, login_manager


class Stance(str, Enum):
    FOR = "for"
    AGAINST = "against"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    confirmed = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    opinions = db.relationship("Opinion", backref="author", lazy=True)
    arguments = db.relationship("Argument", backref="author", lazy=True)
    reasoning = db.relationship("Reasoning", backref="author", lazy=True)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self) -> str:
        serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        return serializer.dumps(self.email)

    def confirm_token(self, token: str, expiration: int = 3600) -> bool:
        serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        try:
            email = serializer.loads(token, max_age=expiration)
        except (SignatureExpired, BadSignature):
            return False
        return email == self.email

    def __repr__(self) -> str:
        return f"<User {self.username}>"


class Opinion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    arguments = db.relationship(
        "Argument", backref="opinion", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Opinion {self.title}>"


class Argument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    stance = db.Column(db.Enum(Stance), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    opinion_id = db.Column(db.Integer, db.ForeignKey("opinion.id"), nullable=False)

    reasoning = db.relationship(
        "Reasoning", backref="argument", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Argument {self.stance.value} on opinion {self.opinion_id}>"


class Reasoning(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    argument_id = db.Column(db.Integer, db.ForeignKey("argument.id"), nullable=False)

    def __repr__(self) -> str:
        return f"<Reasoning by {self.user_id} on argument {self.argument_id}>"


@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))
