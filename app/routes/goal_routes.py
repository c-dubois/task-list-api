from flask import Blueprint, Response, abort, make_response, request
from app.models.goal import Goal
from app.models.task import Task
from app.routes.routes_utilities import validate_model, create_model
from ..db import db

bp = Blueprint("goals_bp", __name__, url_prefix="/goals")


@bp.post("")
def create_goal():
    request_body = request.get_json()
    return create_model(Goal, request_body)

@bp.get("")
def get_goals():
    query = db.select(Goal)

    title_param = request.args.get("title")
    if title_param:
        query = query.where(Goal.title.ilike(f"%{title_param}%"))

    sort_param = request.args.get("sort")
    if sort_param == "asc":
        query = query.order_by(Goal.title.asc())
    elif sort_param == "desc":
        query = query.order_by(Goal.title.desc())
    else:
        query = query.order_by(Goal.id)

    goals = db.session.scalars(query)

    goals_response = []
    for goal in goals:
        goals_response.append(goal.to_dict())

    return goals_response

@bp.get("/<goal_id>")
def get_one_goal(goal_id):
    goal = validate_model(Goal, goal_id)

    return {"goal": goal.to_dict()}

@bp.put("<goal_id>")
def update_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    request_body = request.get_json()

    if "title" in request_body:
        goal.title = request_body["title"]

    db.session.commit()
    return "", 204

@bp.delete("/<goal_id>")
def delete_task(goal_id):
    goal = validate_model(Goal, goal_id)

    db.session.delete(goal)
    db.session.commit()

    return "", 204

@bp.post("/<goal_id>/tasks")
def add_tasks_to_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    request_body = request.get_json()

    if "task_ids" not in request_body:
        abort(make_response({"message": "Missing required field: task_ids"}, 400))

    for task in goal.tasks:
        task.goal_id = None

    tasks = []
    for task_id in request_body["task_ids"]:
        task = validate_model(Task, task_id)
        task.goal_id = goal.id
        tasks.append(task)

    db.session.commit()
    
    return {
        "id": goal.id,
        "task_ids": request_body["task_ids"]
    }

@bp.get("/<goal_id>/tasks")
def get_all_tasks_under_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    
    return {
        "id": goal.id,
        "title": goal.title,
        "tasks": [task.to_dict() for task in goal.tasks]
    }