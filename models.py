from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)

    plans = db.relationship(
        "WorkoutPlan", backref="user", cascade="all, delete-orphan", passive_deletes=True
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.user_id)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
        }

class Exercise(db.Model):
    __tablename__ = "exercises"

    exercise_id = db.Column(db.Integer, primary_key=True)
    exercise_name = db.Column(db.String(100), nullable=False)
    muscle_group = db.Column(db.String(50))

    def to_dict(self):
        return {
            "exercise_id": self.exercise_id,
            "exercise_name": self.exercise_name,
            "muscle_group": self.muscle_group,
        }

class WorkoutPlan(db.Model):
    __tablename__ = "workout_plans"

    plan_id = db.Column(db.Integer, primary_key=True)
    plan_name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )

    sessions = db.relationship(
        "WorkoutSession",
        backref="plan",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def to_dict(self):
        return {
            "plan_id": self.plan_id,
            "plan_name": self.plan_name,
            "user_id": self.user_id,
        }

class WorkoutSession(db.Model):
    __tablename__ = "workout_sessions"

    session_id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(
        db.Integer,
        db.ForeignKey("workout_plans.plan_id", ondelete="CASCADE"),
        nullable=False,
    )
    date = db.Column(db.Date, nullable=False)

    performed_exercises = db.relationship(
        "PerformedExercise",
        backref="session",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "plan_id": self.plan_id,
            "date": self.date.isoformat() if self.date else None,
        }

class PerformedExercise(db.Model):
    __tablename__ = "performed_exercises"

    performed_id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(
        db.Integer,
        db.ForeignKey("workout_sessions.session_id", ondelete="CASCADE"),
        nullable=False,
    )
    exercise_id = db.Column(
        db.Integer,
        db.ForeignKey("exercises.exercise_id", ondelete="RESTRICT"),
        nullable=False,
    )

    exercise = db.relationship("Exercise")
    sets = db.relationship(
        "ExerciseSet",
        backref="performed_exercise",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def to_dict(self):
        return {
            "performed_id": self.performed_id,
            "session_id": self.session_id,
            "exercise_id": self.exercise_id,
        }

class ExerciseSet(db.Model):
    __tablename__ = "exercise_sets"

    set_id = db.Column(db.Integer, primary_key=True)
    performed_id = db.Column(
        db.Integer,
        db.ForeignKey("performed_exercises.performed_id", ondelete="CASCADE"),
        nullable=False,
    )
    set_number = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Numeric(6, 2))
    reps = db.Column(db.Integer)
    time = db.Column(db.Integer)

    def to_dict(self):
        return {
            "set_id": self.set_id,
            "performed_id": self.performed_id,
            "set_number": self.set_number,
            "weight": float(self.weight) if self.weight is not None else None,
            "reps": self.reps,
            "time": self.time,
        }
