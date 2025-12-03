from flask import Blueprint, abort, flash, redirect, render_template, url_for, request
from flask_login import current_user, login_required, logout_user

from app import db
from app.forms import ArgumentForm, OpinionForm, ReasoningForm, ManageUserForm
from app.models import Argument, Opinion, Reasoning, Stance, User
from app.utils import render_markdown

main_bp = Blueprint("main", __name__)


@main_bp.app_template_filter("markdown")
def markdown_filter(text: str) -> str:
    return render_markdown(text)


@main_bp.app_context_processor
def inject_globals():
    return {"Stance": Stance}


@main_bp.before_app_request
def enforce_blocked_user_logout():
    if current_user.is_authenticated and getattr(current_user, "is_blocked", False):
        logout_user()
        flash("Your account has been blocked. Contact an administrator.", "danger")
        return redirect(url_for("auth.login"))


def admin_required():
    if not current_user.is_authenticated or not getattr(current_user, "is_admin", False):
        abort(403)


@main_bp.route("/")
def index():
    opinions = (
        Opinion.query.order_by(Opinion.created_at.desc())
        .limit(50)
        .all()
    )
    return render_template("index.html", opinions=opinions)


@main_bp.route("/opinions/new", methods=["GET", "POST"])
@login_required
def new_opinion():
    form = OpinionForm()
    if form.validate_on_submit():
        opinion = Opinion(
            title=form.title.data,
            content=form.content.data,
            author=current_user,
        )
        argument = Argument(
            content=form.first_argument_content.data,
            stance=Stance(form.first_argument_stance.data),
            author=current_user,
            opinion=opinion,
        )
        reasoning = Reasoning(
            content=form.first_reasoning_content.data,
            author=current_user,
            argument=argument,
        )
        db.session.add_all([opinion, argument, reasoning])
        db.session.commit()
        flash("Opinion and first argument posted.", "success")
        return redirect(url_for("main.view_opinion", opinion_id=opinion.id))
    return render_template("opinions/new.html", form=form)


@main_bp.route("/opinions/<int:opinion_id>")
def view_opinion(opinion_id):
    opinion = Opinion.query.get_or_404(opinion_id)
    arguments_for = Argument.query.filter_by(opinion_id=opinion_id, stance=Stance.FOR).all()
    arguments_against = Argument.query.filter_by(opinion_id=opinion_id, stance=Stance.AGAINST).all()
    return render_template(
        "opinions/detail.html",
        opinion=opinion,
        arguments_for=arguments_for,
        arguments_against=arguments_against,
    )


@main_bp.route("/opinions/<int:opinion_id>/arguments/new", methods=["GET", "POST"])
@login_required
def new_argument(opinion_id):
    opinion = Opinion.query.get_or_404(opinion_id)
    form = ArgumentForm()
    stance_prefill = request.args.get("stance")
    if stance_prefill in [s.value for s in Stance]:
        form.stance.data = stance_prefill
    if form.validate_on_submit():
        argument = Argument(
            content=form.content.data,
            stance=Stance(form.stance.data),
            opinion=opinion,
            author=current_user,
        )
        db.session.add(argument)
        db.session.commit()
        flash("Argument added.", "success")
        return redirect(url_for("main.view_opinion", opinion_id=opinion_id))
    return render_template("arguments/new.html", form=form, opinion=opinion)


@main_bp.route("/arguments/<int:argument_id>")
def view_argument(argument_id):
    argument = Argument.query.get_or_404(argument_id)
    reasoning = Reasoning.query.filter_by(argument_id=argument_id).order_by(Reasoning.created_at.desc()).all()
    return render_template("arguments/detail.html", argument=argument, reasoning=reasoning)


@main_bp.route("/arguments/<int:argument_id>/reasoning/new", methods=["GET", "POST"])
@login_required
def new_reasoning(argument_id):
    argument = Argument.query.get_or_404(argument_id)
    form = ReasoningForm()
    if form.validate_on_submit():
        entry = Reasoning(content=form.content.data, argument=argument, author=current_user)
        db.session.add(entry)
        db.session.commit()
        flash("Reasoning added.", "success")
        return redirect(url_for("main.view_argument", argument_id=argument_id))
    return render_template("reasoning/new.html", form=form, argument=argument)


@main_bp.route("/admin/users", methods=["GET", "POST"])
@login_required
def admin_users():
    admin_required()
    form = ManageUserForm()
    if form.validate_on_submit():
        user = User.query.get(form.user_id.data)
        if not user:
            flash("User not found.", "danger")
            return redirect(url_for("main.admin_users"))
        action = form.action.data
        if user.id == current_user.id and action in {"block", "demote"}:
            flash("You cannot block or demote yourself.", "warning")
            return redirect(url_for("main.admin_users"))

        if action == "promote":
            user.is_admin = True
            flash(f"{user.username} promoted to admin.", "success")
        elif action == "demote":
            user.is_admin = False
            flash(f"{user.username} demoted from admin.", "info")
        elif action == "block":
            user.is_blocked = True
            flash(f"{user.username} has been blocked.", "warning")
        elif action == "unblock":
            user.is_blocked = False
            flash(f"{user.username} has been unblocked.", "success")
        else:
            flash("Unknown action.", "danger")
            return redirect(url_for("main.admin_users"))
        db.session.commit()
        return redirect(url_for("main.admin_users"))

    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=users, form=form)
