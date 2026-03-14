from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.middlewares.auth_middleware import role_required
from app.services.ride_service import request_ride, accept_ride, complete_ride, cancel_ride
from app.database.db_connection import get_db_cursor
from app.utils.response_handler import success_response, error_response
from app.utils.logger import setup_logger

ride_bp = Blueprint("rides", __name__)
logger = setup_logger(__name__)

@ride_bp.route("/request", methods=["POST"])
@jwt_required()
def request_ride_route():
    """
    Request a new ride
    ---
    tags:
      - Rides
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            pickup_location:
              type: string
              example: Location A
            drop_location:
              type: string
              example: Location B
            distance:
              type: number
              example: 10.5
            eco_mode_enabled:
              type: boolean
              example: true
    responses:
      201:
        description: Ride requested successfully
    """
    user_id = int(get_jwt_identity())
    
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT ride_id FROM Rides WHERE user_id = ? AND ride_status IN ('REQUESTED', 'ACCEPTED')",
                (user_id,)
            )
            if cursor.fetchone():
                return error_response("You already have a pending ride. Please complete or cancel it first.")
    except Exception as e:
        logger.error(f"Check pending ride error: {e}")
    
    return request_ride(user_id, request.get_json())


@ride_bp.route("/pending", methods=["GET"])
@role_required("DRIVER")
def get_pending_rides():
    """
    Get all pending rides
    ---
    tags:
      - Rides
    security:
      - Bearer: []
    responses:
      200:
        description: List of pending rides
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT r.ride_id, r.pickup_location, r.drop_location, 
                       r.distance, r.fare, r.created_at, u.name
                FROM Rides r
                JOIN Users u ON r.user_id = u.user_id
                WHERE r.ride_status = 'REQUESTED'
                ORDER BY r.created_at DESC
            """)
            rides = cursor.fetchall()
            
            ride_list = [
                {
                    "ride_id": r[0],
                    "pickup_location": r[1],
                    "drop_location": r[2],
                    "distance": r[3],
                    "fare": float(r[4]) if r[4] else 0,
                    "created_at": str(r[5]),
                    "passenger_name": r[6]
                } for r in rides
            ]
        
        return success_response("Pending rides retrieved", {"rides": ride_list})
    except Exception as e:
        logger.error(f"Get pending rides error: {e}")
        return error_response("Failed to get pending rides", 500)


@ride_bp.route("/<int:ride_id>/accept", methods=["PATCH"])
@role_required("DRIVER")
def accept_ride_route(ride_id):
    """
    Accept a ride
    ---
    tags:
      - Rides
    security:
      - Bearer: []
    parameters:
      - in: path
        name: ride_id
        type: integer
        required: true
    responses:
      200:
        description: Ride accepted successfully
    """
    user_id = int(get_jwt_identity())
    
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT driver_id FROM Drivers WHERE user_id = ?", (user_id,))
            driver = cursor.fetchone()
            if driver:
                cursor.execute(
                    "SELECT ride_id FROM Rides WHERE driver_id = ? AND ride_status = 'ACCEPTED'",
                    (driver[0],)
                )
                if cursor.fetchone():
                    return error_response("You already have an active ride. Complete it first.")
    except Exception as e:
        logger.error(f"Check active ride error: {e}")
    
    return accept_ride(user_id, ride_id)

@ride_bp.route("/<int:ride_id>/complete", methods=["PATCH"])
@role_required("DRIVER")
def complete_ride_route(ride_id):
    """
    Complete a ride
    ---
    tags:
      - Rides
    security:
      - Bearer: []
    parameters:
      - in: path
        name: ride_id
        type: integer
        required: true
    responses:
      200:
        description: Ride completed successfully
    """
    user_id = int(get_jwt_identity())
    return complete_ride(user_id, ride_id)

@ride_bp.route("/<int:ride_id>/cancel", methods=["PATCH"])
@jwt_required()
def cancel_ride_route(ride_id):
    """
    Cancel a ride
    ---
    tags:
      - Rides
    security:
      - Bearer: []
    parameters:
      - in: path
        name: ride_id
        type: integer
        required: true
    responses:
      200:
        description: Ride cancelled successfully
    """
    user_id = get_jwt_identity()
    return cancel_ride(user_id, ride_id)
