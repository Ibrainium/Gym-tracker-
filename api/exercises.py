from api.helpers import make_crud_blueprint
from models import Exercise

FIELDS = {
    "exercise_name": {"type": "string", "required": True, "max_len": 100},
    "muscle_group": {"type": "string", "required": False, "max_len": 50},
}

bp = make_crud_blueprint(
    name="exercises",
    model=Exercise,
    id_field="exercise_id",
    fields=FIELDS,
    url_prefix="/api/exercises",
)
