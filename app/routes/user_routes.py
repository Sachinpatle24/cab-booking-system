from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.user_service import get_profile, get_user_rides

user_bp = Blueprint("users", __name__)

@user_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    """
    Get user profile
    ---
    tags:
      - Users
    security:
      - Bearer: []
    responses:
      200:
        description: User profile retrieved
      401:
        description: Unauthorized
      404:
        description: User not found
    """
    user_id = get_jwt_identity()
    return get_profile(user_id)

@user_bp.route("/rides", methods=["GET"])
@jwt_required()
def rides():
    """
    Get user's ride history
    ---
    tags:
      - Users
    security:
      - Bearer: []
    responses:
      200:
        description: Ride history retrieved
      401:
        description: Unauthorized
    """
    user_id = get_jwt_identity()
    return get_user_rides(user_id)
