from flask import render_template, current_app, url_for
from flask_mail import Message

from app import mail


def build_confirm_url(token: str) -> str:
    """
    Build a confirmation URL. Flask's routing will include the configured prefix automatically.
    """
    return url_for("auth.confirm_email", token=token, _external=True)


def send_email_confirmation(to_email: str, username: str, token: str) -> None:
    confirm_url = build_confirm_url(token)

    msg = Message(
        subject=f"{current_app.config.get('APP_NAME', 'Debate Hub')} - Confirm your email",
        recipients=[to_email],
    )
    msg.body = render_template("email/confirm.txt", username=username, confirm_url=confirm_url)
    msg.html = render_template("email/confirm.html", username=username, confirm_url=confirm_url)
    mail.send(msg)
