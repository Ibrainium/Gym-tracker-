from datetime import date, datetime

from flask import Blueprint, jsonify, request
from flask_login import login_required
from sqlalchemy.exc import IntegrityError

from models import db

class ApiError(Exception):

    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status

def register_error_handlers(app):

    @app.errorhandler(ApiError)
    def handle_api_error(err):
        return jsonify(error=err.message), err.status

    @app.errorhandler(404)
    def handle_404(_err):
        return jsonify(error="Resource not found"), 404

    @app.errorhandler(405)
    def handle_405(_err):
        return jsonify(error="Method not allowed"), 405

    @app.errorhandler(500)
    def handle_500(_err):
        db.session.rollback()
        return jsonify(error="Internal server error"), 500

def _coerce(field, spec, value):
    required = spec.get("required", False)

    if value is None or (isinstance(value, str) and value.strip() == ""):
        if required:
            raise ApiError(f"'{field}' is required")
        return None

    ftype = spec["type"]
    try:
        if ftype == "string":
            value = str(value).strip()
            max_len = spec.get("max_len")
            if max_len and len(value) > max_len:
                raise ApiError(f"'{field}' must be at most {max_len} characters")
        elif ftype == "integer":
            value = int(value)
        elif ftype == "number":
            value = float(value)
        elif ftype == "date":
            value = datetime.strptime(str(value), "%Y-%m-%d").date()
        else:
            raise ApiError(f"Unknown field type for '{field}'")
    except (ValueError, TypeError):
        raise ApiError(f"'{field}' has an invalid value for type {ftype}")

    minimum = spec.get("min")
    if minimum is not None and value < minimum:
        raise ApiError(f"'{field}' must be >= {minimum}")

    if "fk" in spec:
        ref_model, ref_col = spec["fk"]
        exists = db.session.get(ref_model, value)
        if exists is None:
            raise ApiError(f"{field}={value} does not exist")

    return value

def _build_payload(fields, data, *, partial):
    if not isinstance(data, dict):
        raise ApiError("Request body must be a JSON object")

    payload = {}
    for field, spec in fields.items():
        if partial and field not in data:
            continue
        payload[field] = _coerce(field, spec, data.get(field))
    return payload

def make_crud_blueprint(
    name,
    model,
    id_field,
    fields,
    url_prefix,
    scope_query=None,
    owns=None,
    prepare_create=None,
):
    bp = Blueprint(name, __name__, url_prefix=url_prefix)

    singular = name[:-1] if name.endswith("s") else name

    def get_or_404(item_id):
        obj = db.session.get(model, item_id)
        if obj is None or (owns is not None and not owns(obj)):
            raise ApiError(f"{singular} {item_id} not found", status=404)
        return obj

    @bp.get("")
    @login_required
    def list_items():
        query = db.session.query(model)
        if scope_query is not None:
            query = scope_query(query)
        items = query.order_by(getattr(model, id_field)).all()
        return jsonify([i.to_dict() for i in items])

    @bp.get("/<int:item_id>")
    @login_required
    def get_item(item_id):
        return jsonify(get_or_404(item_id).to_dict())

    @bp.post("")
    @login_required
    def create_item():
        payload = _build_payload(fields, request.get_json(silent=True), partial=False)
        if prepare_create is not None:
            prepare_create(payload)
        obj = model(**payload)
        db.session.add(obj)
        _commit()
        return jsonify(obj.to_dict()), 201

    @bp.put("/<int:item_id>")
    @login_required
    def update_item(item_id):
        obj = get_or_404(item_id)
        payload = _build_payload(fields, request.get_json(silent=True), partial=True)
        for key, value in payload.items():
            setattr(obj, key, value)
        _commit()
        return jsonify(obj.to_dict())

    @bp.delete("/<int:item_id>")
    @login_required
    def delete_item(item_id):
        obj = get_or_404(item_id)
        db.session.delete(obj)
        _commit(
            on_integrity="Cannot delete: other records still reference this item."
        )
        return jsonify(deleted=item_id)

    return bp

def _commit(on_integrity="A database constraint was violated "
                          "(duplicate value or invalid reference)."):
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ApiError(on_integrity, status=409)
