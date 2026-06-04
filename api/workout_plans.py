from flask_login import current_user

from api.helpers import make_crud_blueprint
from models import WorkoutPlan

FIELDS = {
    "plan_name": {"type": "string", "required": True, "max_len": 100},
}

def scope_query(query):
    return query.filter(WorkoutPlan.user_id == current_user.user_id)

def owns(obj):
    return obj.user_id == current_user.user_id

def prepare_create(payload):
    payload["user_id"] = current_user.user_id

bp = make_crud_blueprint(
    name="workout_plans",
    model=WorkoutPlan,
    id_field="plan_id",
    fields=FIELDS,
    url_prefix="/api/workout_plans",
    scope_query=scope_query,
    owns=owns,
    prepare_create=prepare_create,
)
