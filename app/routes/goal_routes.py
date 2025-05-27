from flask import Blueprint, Response, abort, make_response, request
from app.models.task import Task
from app.routes.routes_utilities import validate_model, create_model
from ..db import db

bp = Blueprint("goals_bp", __name__, url_prefix="/goals")