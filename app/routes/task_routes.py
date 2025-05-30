from datetime import datetime
import requests
import os
from dotenv import load_dotenv
from flask import Blueprint, Response, abort, make_response, request
from app.models.task import Task
from app.routes.routes_utilities import validate_model, create_model
from ..db import db

load_dotenv() 

bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@bp.post("")
def create_task():
    request_body = request.get_json()
    return create_model(Task, request_body)

@bp.get("")
def get_tasks():
    query = db.select(Task)

    title_param = request.args.get("title")
    if title_param:
        query = query.where(Task.title.ilike(f"%{title_param}%"))

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

@bp.get("/<task_id>")
def get_one_task(task_id):
    task = validate_model(Task, task_id)

    return {"task": task.to_dict()}
    
@bp.put("<task_id>")
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

@bp.delete("/<task_id>")
def delete_task(task_id):
    task = validate_model(Task, task_id)

    db.session.delete(task)
    db.session.commit()

    return "", 204

@bp.patch("/<task_id>/mark_complete")
def mark_task_complete(task_id):
    task = validate_model(Task, task_id)

    task.completed_at = datetime.now()
    db.session.commit()

    slackbot_token = os.environ.get("SLACKBOT_TOKEN")
    # if not slackbot_token:
    #     print("no token found")
    #     return "", 204
    
    message_text = f"Someone just completed the task \"{task.title}\""
    slack_url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {slackbot_token}"
    }
    payload = {
        "channel": "test-slack-api",
        "text": message_text
    }

    try:
        response = requests.post(slack_url, headers=headers, json=payload)
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Slack notification: {str(e)}")

    return "", 204

@bp.patch("/<task_id>/mark_incomplete")
def mark_task_incomplete(task_id):
    task = validate_model(Task, task_id)

    task.completed_at = None
    db.session.commit()

    return "", 204