import re
from datetime import date

from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required

from api import exercise_sets as es_api
from api import exercises as ex_api
from api import performed_exercises as pe_api
from api import workout_plans as wp_api
from api import workout_sessions as ws_api
from api.helpers import ApiError, _build_payload, _commit
from models import (
    Exercise,
    ExerciseSet,
    PerformedExercise,
    WorkoutPlan,
    WorkoutSession,
    db,
)

bp = Blueprint("pages", __name__)

def _matches(pattern, text):
    try:
        return re.search(pattern, text, re.IGNORECASE) is not None
    except re.error:
        return pattern.lower() in text.lower()

def _form_from_item(item, fields):
    out = {}
    for field in fields:
        value = getattr(item, field, None)
        if value is None:
            out[field] = ""
        elif isinstance(value, date):
            out[field] = value.isoformat()
        else:
            out[field] = value
    return out

def register(*, name, path, model, id_field, fields, template, search_text,
             scope_query=None, owns=None, prepare=None, options_query=None):
    scope = scope_query or (lambda query: query)
    is_owner = owns or (lambda obj: True)
    prep = prepare or (lambda payload: None)
    option_builders = options_query or {}

    def build_options():
        return {key: builder() for key, builder in option_builders.items()}

    def show(*, edit_id=None, form=None, error=None, status=200):
        rows = (
            scope(db.session.query(model))
            .order_by(getattr(model, id_field))
            .all()
        )
        q = (request.args.get("q") or "").strip()
        if q:
            rows = [r for r in rows if _matches(q, search_text(r))]

        item = None
        if edit_id is not None:
            candidate = db.session.get(model, edit_id)
            if candidate is not None and is_owner(candidate):
                item = candidate

        if form is None:
            form = _form_from_item(item, fields) if item else {}

        html = render_template(
            template,
            rows=rows,
            q=q,
            editing=item is not None,
            edit_id=(getattr(item, id_field) if item else None),
            form=form,
            error=error,
            options=build_options(),
        )
        return (html, status) if status != 200 else html

    def list_view():
        return show(edit_id=request.args.get("edit", type=int))

    def create_view():
        data = request.form.to_dict()
        try:
            payload = _build_payload(fields, data, partial=False)
            prep(payload)
            db.session.add(model(**payload))
            _commit()
        except ApiError as err:
            return show(form=data, error=err.message, status=400)
        return redirect(url_for(f"pages.{name}_list"))

    def update_view(id):
        obj = db.session.get(model, id)
        if obj is None or not is_owner(obj):
            return show(error="Record not found.", status=404)
        data = request.form.to_dict()
        try:
            payload = _build_payload(fields, data, partial=True)
            prep(payload)
            for key, value in payload.items():
                setattr(obj, key, value)
            _commit()
        except ApiError as err:
            return show(edit_id=id, form=data, error=err.message, status=400)
        return redirect(url_for(f"pages.{name}_list"))

    def delete_view(id):
        obj = db.session.get(model, id)
        if obj is None or not is_owner(obj):
            return show(error="Record not found.", status=404)
        db.session.delete(obj)
        try:
            _commit(on_integrity="Cannot delete: other records still use this.")
        except ApiError as err:
            return show(error=err.message, status=409)
        return redirect(url_for(f"pages.{name}_list"))

    bp.add_url_rule(path, endpoint=f"{name}_list",
                    view_func=login_required(list_view), methods=["GET"])
    bp.add_url_rule(path, endpoint=f"{name}_create",
                    view_func=login_required(create_view), methods=["POST"])
    bp.add_url_rule(f"{path}/<int:id>", endpoint=f"{name}_update",
                    view_func=login_required(update_view), methods=["POST"])
    bp.add_url_rule(f"{path}/<int:id>/delete", endpoint=f"{name}_delete",
                    view_func=login_required(delete_view), methods=["POST"])

register(
    name="exercises", path="/exercises", model=Exercise, id_field="exercise_id",
    fields=ex_api.FIELDS, template="exercises.html",
    search_text=lambda e: f"{e.exercise_id} {e.exercise_name} {e.muscle_group or ''}",
)

register(
    name="workout_plans", path="/workout-plans", model=WorkoutPlan,
    id_field="plan_id", fields=wp_api.FIELDS, template="workout_plans.html",
    scope_query=wp_api.scope_query, owns=wp_api.owns, prepare=wp_api.prepare_create,
    search_text=lambda p: f"{p.plan_id} {p.plan_name}",
)

register(
    name="workout_sessions", path="/workout-sessions", model=WorkoutSession,
    id_field="session_id", fields=ws_api.FIELDS, template="workout_sessions.html",
    scope_query=ws_api.scope_query, owns=ws_api.owns, prepare=ws_api.prepare_create,
    search_text=lambda s: f"{s.session_id} {s.plan.plan_name if s.plan else ''} {s.date}",
    options_query={
        "plans": lambda: wp_api.scope_query(db.session.query(WorkoutPlan))
        .order_by(WorkoutPlan.plan_name).all(),
    },
)

register(
    name="performed_exercises", path="/performed-exercises",
    model=PerformedExercise, id_field="performed_id", fields=pe_api.FIELDS,
    template="performed_exercises.html",
    scope_query=pe_api.scope_query, owns=pe_api.owns, prepare=pe_api.prepare_create,
    search_text=lambda pe: f"{pe.performed_id} "
                           f"{pe.exercise.exercise_name if pe.exercise else ''} "
                           f"{pe.session.date if pe.session else ''}",
    options_query={
        "sessions": lambda: ws_api.scope_query(db.session.query(WorkoutSession))
        .order_by(WorkoutSession.date).all(),
        "exercises": lambda: db.session.query(Exercise)
        .order_by(Exercise.exercise_name).all(),
    },
)

register(
    name="exercise_sets", path="/exercise-sets", model=ExerciseSet,
    id_field="set_id", fields=es_api.FIELDS, template="exercise_sets.html",
    scope_query=es_api.scope_query, owns=es_api.owns, prepare=es_api.prepare_create,
    search_text=lambda s: f"{s.set_id} #{s.performed_id} {s.set_number} "
                          f"{s.weight or ''} {s.reps or ''} {s.time or ''}",
    options_query={
        "performed": lambda: pe_api.scope_query(db.session.query(PerformedExercise))
        .order_by(PerformedExercise.performed_id).all(),
    },
)
