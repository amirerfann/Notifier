from flask import Blueprint

bp = Blueprint('main', __name__)

from app.main import routes # Import at the bottom to avoid circular dependencies
