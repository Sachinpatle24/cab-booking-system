from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.ride_service import request_ride, accept_ride, complete_ride, cancel_ride
from app.database.db_connection import get_db_cursor
from app.utils.response_handler import success_response, error_response


ride_bp = Blueprint("rides", __name__)

@ride_bp.route("/request", methods=["POST"])
@jwt_required()
def request_ride_route():
    """Request a new ride"""
    user_id = int(get_jwt_identity())
    
    # Check if user has pending ride
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT ride_id FROM Rides WHERE user_id = ? AND ride_status IN ('REQUESTED', 'ACCEPTED')",
                (user_id,)
            )
            if cursor.fetchone():
                return error_response("You already have a pending ride. Please complete or cancel it first.")
    except:
        pass
    
    return request_ride(user_id, request.get_json())


@ride_bp.route("/pending", methods=["GET"])
def get_pending_rides():
    """Get all pending rides for drivers"""
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
        return error_response("Failed to get pending rides", 500)


@ride_bp.route("/<int:ride_id>/accept", methods=["PATCH"])
@jwt_required()
def accept_ride_route(ride_id):
    """Accept a ride (Driver only)"""
    user_id = int(get_jwt_identity())
    
    # Check if driver has active ride
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
    except:
        pass
    
    return accept_ride(user_id, ride_id)

@ride_bp.route("/<int:ride_id>/complete", methods=["PATCH"])
@jwt_required()
def complete_ride_route(ride_id):
    """Complete a ride"""
    return complete_ride(ride_id)

@ride_bp.route("/<int:ride_id>/cancel", methods=["PATCH"])
@jwt_required()
def cancel_ride_route(ride_id):
    """Cancel a ride"""
    user_id = get_jwt_identity()
    return cancel_ride(user_id, ride_id)
