from flask_login import current_user

from api.helpers import ApiError, make_crud_blueprint
from models import (
    Exercise,
    PerformedExercise,
    WorkoutPlan,
    WorkoutSession,
    db,
)

FIELDS = {
    "session_id": {
        "type": "integer",
        "required": True,
        "fk": (WorkoutSession, "session_id"),
    },
    "exercise_id": {
        "type": "integer",
        "required": True,
        "fk": (Exercise, "exercise_id"),
    },
}

def scope_query(query):
    return (
        query.join(WorkoutSession, PerformedExercise.session_id == WorkoutSession.session_id)
        .join(WorkoutPlan, WorkoutSession.plan_id == WorkoutPlan.plan_id)
        .filter(WorkoutPlan.user_id == current_user.user_id)
    )

def owns(obj):
    return (
        obj.session is not None
        and obj.session.plan is not None
        and obj.session.plan.user_id == current_user.user_id
    )

def prepare_create(payload):
    session = db.session.get(WorkoutSession, payload["session_id"])
    if session is None or session.plan.user_id != current_user.user_id:
        raise ApiError("session_id does not exist", status=400)

bp = make_crud_blueprint(
    name="performed_exercises",
    model=PerformedExercise,
    id_field="performed_id",
    fields=FIELDS,
    url_prefix="/api/performed_exercises",
    scope_query=scope_query,
    owns=owns,
    prepare_create=prepare_create,
)
