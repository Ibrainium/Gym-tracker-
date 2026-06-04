from flask_login import current_user

from api.helpers import ApiError, make_crud_blueprint
from models import (
    ExerciseSet,
    PerformedExercise,
    WorkoutPlan,
    WorkoutSession,
    db,
)

FIELDS = {
    "performed_id": {
        "type": "integer",
        "required": True,
        "fk": (PerformedExercise, "performed_id"),
    },
    "set_number": {"type": "integer", "required": True, "min": 1},
    "weight": {"type": "number", "required": False, "min": 0},
    "reps": {"type": "integer", "required": False, "min": 0},
    "time": {"type": "integer", "required": False, "min": 0},
}

def scope_query(query):
    return (
        query.join(PerformedExercise, ExerciseSet.performed_id == PerformedExercise.performed_id)
        .join(WorkoutSession, PerformedExercise.session_id == WorkoutSession.session_id)
        .join(WorkoutPlan, WorkoutSession.plan_id == WorkoutPlan.plan_id)
        .filter(WorkoutPlan.user_id == current_user.user_id)
    )

def owns(obj):
    pe = obj.performed_exercise
    return (
        pe is not None
        and pe.session is not None
        and pe.session.plan is not None
        and pe.session.plan.user_id == current_user.user_id
    )

def prepare_create(payload):
    pe = db.session.get(PerformedExercise, payload["performed_id"])
    if pe is None or pe.session.plan.user_id != current_user.user_id:
        raise ApiError("performed_id does not exist", status=400)

bp = make_crud_blueprint(
    name="exercise_sets",
    model=ExerciseSet,
    id_field="set_id",
    fields=FIELDS,
    url_prefix="/api/exercise_sets",
    scope_query=scope_query,
    owns=owns,
    prepare_create=prepare_create,
)
