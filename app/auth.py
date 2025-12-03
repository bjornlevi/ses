from flask import Blueprint, flash, redirect, render_template, request, url_for, current_app
from flask_login import current_user, login_required, login_user, logout_user

from app import db
from app.email_utils import send_email_confirmation
from app.forms import LoginForm, RegisterForm
from app.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data.lower(),
            username=form.username.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        token = user.generate_confirmation_token()
        send_email_confirmation(user.email, user.username, token)

        flash("Account created. Please check your email to confirm your address.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            if user.is_blocked:
                flash("This account is blocked. Contact an administrator.", "danger")
                return redirect(url_for("auth.login"))
            if not user.confirmed:
                flash("Please confirm your email to continue.", "warning")
                return redirect(url_for("auth.login"))
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.index"))
        flash("Invalid email or password.", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/confirm/<token>")
def confirm_email(token):
    from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        email = serializer.loads(token, max_age=3600)
    except (BadSignature, SignatureExpired):
        email = None

    if not email:
        flash("Confirmation link is invalid or expired.", "danger")
        return redirect(url_for("main.index"))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash("Account not found for this confirmation link.", "danger")
        return redirect(url_for("main.index"))

    if user.confirmed:
        flash("Your email is already confirmed.", "info")
        return redirect(url_for("main.index"))

    user.confirmed = True
    db.session.commit()
    flash("Email confirmed. You can now participate.", "success")
    return redirect(url_for("auth.login"))
