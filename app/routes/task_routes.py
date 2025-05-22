from flask import Blueprint, Response, abort, make_response, request
from app.models.task import Task
from app.routes.routes_utilities import validate_model, create_model
from ..db import db

task_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@task_bp.post("")
def create_task():
    request_body = request.get_json()
    return create_model(Task, request_body)

@task_bp.get("")
def get_tasks():
    query = db.select(Task)

    name_param = request.args.get("title")
    if name_param:
        query = query.where(Task.title.ilike(f"%{name_param}%"))

    description_param = request.args.get("description")
    if description_param:
        query = query.where(Task.description.ilike(f"%{description_param}%"))

    completed_at_param = request.args.get("completed_at")
    if completed_at_param:
        query = query.where(Task.completed_at.ilike(f"%{completed_at_param}%"))

    sort_param = request.args.get("sort")
    if sort_param == "asc":
        query = query.order_by(Task.title.asc())
    elif sort_param == "desc":
        query = query.order_by(Task.title.desc())
    else:
        query = query.order_by(Task.id)

    tasks = db.session.scalars(query)

    tasks_response = []
    for task in tasks:
        tasks_response.append(task.to_dict())

    return tasks_response

@task_bp.get("/<task_id>")
def get_one_task(task_id):
    task = validate_model(Task, task_id)

    return {"task": task.to_dict()}
    
@task_bp.put("<task_id>")
def update_task(task_id):
    task = validate_model(Task, task_id)
    request_body = request.get_json()

    if "title" in request_body:
        task.title = request_body["title"]
    if "description" in request_body:
        task.description = request_body["description"]
    if "completed_at" in request_body:
        task.completed_at = request_body["completed_at"]

    db.session.commit()
    return "", 204
# Another option is to return this: Response(status=204, mimetype="application/json")

@task_bp.delete("/<task_id>")
def delete_task(task_id):
    task = validate_model(Task, task_id)

    db.session.delete(task)
    db.session.commit()

    return "", 204