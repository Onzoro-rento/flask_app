from flask import Blueprint

plans_bp = Blueprint('plans', __name__)

from . import routes
