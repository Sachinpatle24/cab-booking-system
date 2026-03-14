from flask import Blueprint
from app.middlewares.auth_middleware import role_required
from app.services.admin_service import get_stats, get_all_users, get_all_rides

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/stats", methods=["GET"])
@role_required("ADMIN")
def stats():
    """
    Get admin statistics
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    responses:
      200:
        description: Statistics retrieved
    """
    return get_stats()

@admin_bp.route("/users", methods=["GET"])
@role_required("ADMIN")
def users():
    """
    Get all users
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    responses:
      200:
        description: Users retrieved
    """
    return get_all_users()

@admin_bp.route("/rides", methods=["GET"])
@role_required("ADMIN")
def rides():
    """
    Get all rides
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    responses:
      200:
        description: Rides retrieved
    """
    return get_all_rides()
