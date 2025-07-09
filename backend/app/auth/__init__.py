from flask import Blueprint

bp = Blueprint('auth', __name__)

from app.auth import routes # Import routes at the bottom to avoid circular dependencies
