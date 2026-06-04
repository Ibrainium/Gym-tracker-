from datetime import timedelta

import click
from flask import Flask, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_required
from flask_wtf.csrf import CSRFError, CSRFProtect

import auth
import views
from api.helpers import register_error_handlers
from config import Config
from models import (
    Exercise,
    ExerciseSet,
    PerformedExercise,
    User,
    WorkoutPlan,
    WorkoutSession,
    db,
)

login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.config.setdefault("PERMANENT_SESSION_LIFETIME", timedelta(minutes=30))
    app.config.setdefault("WTF_CSRF_TIME_LIMIT", None)
    app.config.setdefault("SESSION_COOKIE_HTTPONLY", True)
    app.config.setdefault("SESSION_COOKIE_SAMESITE", "Lax")

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    register_error_handlers(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized():
        return redirect(url_for("auth.login", next=request.path))

    @app.errorhandler(CSRFError)
    def handle_csrf_error(err):
        return (
            render_template(
                "login.html", error="Your session expired. Please try again."
            ),
            400,
        )

    app.register_blueprint(auth.bp)
    app.register_blueprint(views.bp)

    @app.get("/")
    @login_required
    def page_index():
        uid = current_user.user_id

        def scoped_count(query):
            return query.filter(WorkoutPlan.user_id == uid).count()

        counts = {
            "workout_plans": db.session.query(WorkoutPlan)
            .filter(WorkoutPlan.user_id == uid).count(),
            "workout_sessions": scoped_count(
                db.session.query(WorkoutSession)
                .join(WorkoutPlan, WorkoutSession.plan_id == WorkoutPlan.plan_id)
            ),
            "performed_exercises": scoped_count(
                db.session.query(PerformedExercise)
                .join(WorkoutSession, PerformedExercise.session_id == WorkoutSession.session_id)
                .join(WorkoutPlan, WorkoutSession.plan_id == WorkoutPlan.plan_id)
            ),
            "exercise_sets": scoped_count(
                db.session.query(ExerciseSet)
                .join(PerformedExercise, ExerciseSet.performed_id == PerformedExercise.performed_id)
                .join(WorkoutSession, PerformedExercise.session_id == WorkoutSession.session_id)
                .join(WorkoutPlan, WorkoutSession.plan_id == WorkoutPlan.plan_id)
            ),
            "exercises": db.session.query(Exercise).count(),
        }
        return render_template("index.html", counts=counts)

    _register_cli(app)
    return app

def _register_cli(app):

    @app.cli.command("create-user")
    @click.argument("username")
    @click.argument("email")
    @click.argument("password")
    def create_user(username, email, password):
        if db.session.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first():
            click.echo("A user with that username or email already exists.")
            return
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f"Created user '{username}' (id {user.user_id}).")

    @app.cli.command("list-users")
    def list_users():
        for u in db.session.query(User).order_by(User.user_id):
            click.echo(f"{u.user_id}\t{u.username}\t{u.email}")

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)
