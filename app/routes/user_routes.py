from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database.db_connection import get_db_cursor
from app.utils.response_handler import success_response, error_response
from app.utils.logger import setup_logger

user_bp = Blueprint("users", __name__)
logger = setup_logger(__name__)

@user_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
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
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            data:
              type: object
              properties:
                profile:
                  type: object
                  properties:
                    user_id:
                      type: integer
                    name:
                      type: string
                    email:
                      type: string
                    role:
                      type: string
                    eco_score:
                      type: integer
      401:
        description: Unauthorized
      404:
        description: User not found
    """
    try:
        user_id = get_jwt_identity()
        
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT user_id, name, email, role, eco_score FROM Users WHERE user_id = ?",
                (user_id,)
            )
            user = cursor.fetchone()
            
            if not user:
                return error_response("User not found", 404)
            
            profile = {
                "user_id": user[0],
                "name": user[1],
                "email": user[2],
                "role": user[3],
                "eco_score": user[4]
            }
        
        return success_response("Profile retrieved", {"profile": profile})
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        return error_response("Failed to get profile", 500)

@user_bp.route("/rides", methods=["GET"])
@jwt_required()
def get_user_rides():
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
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            data:
              type: object
              properties:
                rides:
                  type: array
                  items:
                    type: object
      401:
        description: Unauthorized
    """
    try:
        user_id = get_jwt_identity()
        
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT r.ride_id, r.pickup_location, r.drop_location, 
                       r.distance, r.fare, r.ride_status, r.created_at
                FROM Rides r
                WHERE r.user_id = ?
                ORDER BY r.created_at DESC
            """, (user_id,))
            rides = cursor.fetchall()
            
            ride_list = [
                {
                    "ride_id": r[0],
                    "pickup_location": r[1],
                    "drop_location": r[2],
                    "distance": r[3],
                    "fare": float(r[4]) if r[4] else 0,
                    "ride_status": r[5],
                    "created_at": str(r[6])
                } for r in rides
            ]
        
        return success_response("Ride history retrieved", {"rides": ride_list})
    except Exception as e:
        logger.error(f"Get user rides error: {e}")
        return error_response("Failed to get rides", 500)
