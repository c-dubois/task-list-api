from flask import abort, make_response
from ..db import db

def validate_model(cls, model_id):
    try:
        model_id = int(model_id)
    except ValueError:
        invalid_response = {{"message": f"The {cls.__name__} with ID {model_id} is invalid."}}
        abort(make_response(invalid_response, 400))

    query = db.select(cls).where(cls.id == model_id)
    model = db.session.scalar(query)

    if not model:
        response = {"message": f"The {cls.__name__} with ID {model_id} is not found."}
        abort(make_response(response, 404))

    return model

def create_model(cls, model_data):
    required_fields = {
        "Task": ["title", "description"],
        "Goal": ["title"]
    }

    missing_fields = [field for field in required_fields[cls.__name__] if field not in model_data]
    if missing_fields:
        abort(make_response({"details": f"Missing required field(s): {', '.join(missing_fields)}"}, 400))

    try:
        new_model = cls.from_dict(model_data)
    except KeyError as error:
        response = {"message": f"Invalid request: missing {error.args[0]}"}
        abort(make_response(response, 400))

    db.session.add(new_model)
    db.session.commit()

    return {f"{cls.__name__.lower()}": new_model.to_dict()}, 201