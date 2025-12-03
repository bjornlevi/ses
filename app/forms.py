from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    HiddenField,
    PasswordField,
    StringField,
    SubmitField,
    TextAreaField,
    SelectField,
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from app.models import User, Stance


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    username = StringField("Username", validators=[DataRequired(), Length(max=80)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )
    submit = SubmitField("Create Account")

    def validate_email(self, email):
        if User.query.filter_by(email=email.data.lower()).first():
            raise ValidationError("Email already registered.")

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError("Username already taken.")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Log In")


class OpinionForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=160)])
    content = TextAreaField(
        "Opinion (Markdown supported)", validators=[DataRequired(), Length(max=5000)]
    )
    first_argument_stance = SelectField(
        "Your first argument stance",
        choices=[(Stance.FOR.value, "For"), (Stance.AGAINST.value, "Against")],
        validators=[DataRequired()],
    )
    first_argument_content = TextAreaField(
        "Argument (Markdown supported)", validators=[DataRequired(), Length(max=4000)]
    )
    first_reasoning_content = TextAreaField(
        "Reasoning for this argument (Markdown supported)",
        validators=[DataRequired(), Length(max=4000)],
    )
    submit = SubmitField("Post Opinion")


class ArgumentForm(FlaskForm):
    stance = SelectField(
        "Stance",
        choices=[(Stance.FOR.value, "For"), (Stance.AGAINST.value, "Against")],
        validators=[DataRequired()],
    )
    content = TextAreaField(
        "Argument (Markdown supported)", validators=[DataRequired(), Length(max=4000)]
    )
    submit = SubmitField("Add Argument")


class ReasoningForm(FlaskForm):
    content = TextAreaField(
        "Reasoning (Markdown supported)", validators=[DataRequired(), Length(max=4000)]
    )
    submit = SubmitField("Add Reasoning")


class ManageUserForm(FlaskForm):
    user_id = HiddenField("User ID", validators=[DataRequired()])
    action = HiddenField("Action", validators=[DataRequired()])
    submit = SubmitField("Apply")
