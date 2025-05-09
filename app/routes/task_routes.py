from flask import Blueprint, Response, abort, make_response, request
from app.models.task import Task


bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@bp.post("")
def create_task():
    request_body = request.get_json()