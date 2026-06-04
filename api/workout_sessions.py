from flask_login import current_user

from api.helpers import ApiError, make_crud_blueprint
from models import WorkoutPlan, WorkoutSession, db

FIELDS = {
    "plan_id": {"type": "integer", "required": True, "fk": (WorkoutPlan, "plan_id")},
    "date": {"type": "date", "required": True},
}

def scope_query(query):
    return (
        query.join(WorkoutPlan, WorkoutSession.plan_id == WorkoutPlan.plan_id)
        .filter(WorkoutPlan.user_id == current_user.user_id)
    )

def owns(obj):
    return obj.plan is not None and obj.plan.user_id == current_user.user_id

def prepare_create(payload):
    plan = db.session.get(WorkoutPlan, payload["plan_id"])
    if plan is None or plan.user_id != current_user.user_id:
        raise ApiError("plan_id does not exist", status=400)

bp = make_crud_blueprint(
    name="workout_sessions",
    model=WorkoutSession,
    id_field="session_id",
    fields=FIELDS,
    url_prefix="/api/workout_sessions",
    scope_query=scope_query,
    owns=owns,
    prepare_create=prepare_create,
)
