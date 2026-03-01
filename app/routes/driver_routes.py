from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database.db_connection import get_db_cursor
from app.utils.response_handler import success_response, error_response
from app.utils.logger import setup_logger

driver_bp = Blueprint("drivers", __name__)
logger = setup_logger(__name__)

@driver_bp.route("/status", methods=["PATCH"])
@jwt_required()
def update_status():
    """
    Update driver status
    ---
    tags:
      - Drivers
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            status:
              type: string
              enum: [AVAILABLE, BUSY, OFFLINE]
    responses:
      200:
        description: Status updated
    """
    try:
        user_id = get_jwt_identity()
        status = request.json.get('status', '').upper()
        
        if status not in ['AVAILABLE', 'BUSY', 'OFFLINE']:
            return error_response("Invalid status. Must be AVAILABLE, BUSY, or OFFLINE")
        
        with get_db_cursor() as cursor:
            cursor.execute("SELECT driver_id FROM Drivers WHERE user_id = ?", (user_id,))
            driver = cursor.fetchone()
            
            if not driver:
                return error_response("User is not a driver", 403)
            
            cursor.execute(
                "UPDATE Drivers SET availability_status = ? WHERE user_id = ?",
                (status, user_id)
            )
        
        logger.info(f"Driver (user {user_id}) status updated to {status}")
        return success_response(f"Status updated to {status}")
    except Exception as e:
        logger.error(f"Update status error: {e}")
        return error_response("Failed to update status", 500)

@driver_bp.route("/rides", methods=["GET"])
@jwt_required()
def get_driver_rides():
    """
    Get driver's rides
    ---
    tags:
      - Drivers
    security:
      - Bearer: []
    responses:
      200:
        description: Driver rides retrieved
    """
    try:
        user_id = get_jwt_identity()
        
        with get_db_cursor() as cursor:
            cursor.execute("SELECT driver_id FROM Drivers WHERE user_id = ?", (user_id,))
            driver = cursor.fetchone()
            
            if not driver:
                return error_response("User is not a driver", 403)
            
            driver_id = driver[0]
            
            cursor.execute("""
                SELECT r.ride_id, r.pickup_location, r.drop_location, 
                       r.distance, r.fare, r.ride_status, r.created_at, u.name
                FROM Rides r
                JOIN Users u ON r.user_id = u.user_id
                WHERE r.driver_id = ?
                ORDER BY r.created_at DESC
            """, (driver_id,))
            rides = cursor.fetchall()
            
            ride_list = [
                {
                    "ride_id": r[0],
                    "pickup_location": r[1],
                    "drop_location": r[2],
                    "distance": r[3],
                    "fare": float(r[4]) if r[4] else 0,
                    "ride_status": r[5],
                    "created_at": str(r[6]),
                    "passenger_name": r[7]
                } for r in rides
            ]
        
        return success_response("Driver rides retrieved", {"rides": ride_list})
    except Exception as e:
        logger.error(f"Get driver rides error: {e}")
        return error_response("Failed to get driver rides", 500)

@driver_bp.route("/earnings", methods=["GET"])
@jwt_required()
def get_driver_earnings():
    """
    Get driver's earnings
    ---
    tags:
      - Drivers
    security:
      - Bearer: []
    responses:
      200:
        description: Earnings retrieved
    """
    try:
        user_id = get_jwt_identity()
        
        with get_db_cursor() as cursor:
            cursor.execute("SELECT driver_id FROM Drivers WHERE user_id = ?", (user_id,))
            driver = cursor.fetchone()
            
            if not driver:
                return error_response("User is not a driver", 403)
            
            driver_id = driver[0]
            
            cursor.execute("""
                SELECT COUNT(*), ISNULL(SUM(fare), 0)
                FROM Rides
                WHERE driver_id = ? AND ride_status = 'COMPLETED'
            """, (driver_id,))
            result = cursor.fetchone()
            
            earnings_data = {
                "completed_rides": result[0],
                "total_earnings": float(result[1])
            }
        
        return success_response("Earnings retrieved", earnings_data)
    except Exception as e:
        logger.error(f"Get earnings error: {e}")
        return error_response("Failed to get earnings", 500)

@driver_bp.route("/available", methods=["GET"])
def get_available_drivers():
    """
    Get available drivers
    ---
    tags:
      - Drivers
    responses:
      200:
        description: Available drivers retrieved
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT d.driver_id, u.name, c.vehicle_number, c.vehicle_type 
                FROM Drivers d 
                JOIN Users u ON d.user_id = u.user_id 
                LEFT JOIN Cabs c ON d.driver_id = c.driver_id 
                WHERE d.availability_status = 'AVAILABLE'
            """)
            drivers = cursor.fetchall()
            
            driver_list = [
                {
                    "driver_id": d[0],
                    "name": d[1],
                    "vehicle_number": d[2],
                    "vehicle_type": d[3]
                } for d in drivers
            ]
        
        return success_response("Available drivers retrieved", {"drivers": driver_list})
    except Exception as e:
        logger.error(f"Get available drivers error: {e}")
        return error_response("Failed to get drivers", 500)

@driver_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_driver_profile():
    """
    Get driver profile
    ---
    tags:
      - Drivers
    security:
      - Bearer: []
    responses:
      200:
        description: Profile retrieved
    """
    try:
        user_id = get_jwt_identity()
        
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT d.driver_id, u.name, u.email, d.license_number, 
                       d.availability_status, c.vehicle_number, c.vehicle_type, d.rating, d.total_ratings
                FROM Drivers d
                JOIN Users u ON d.user_id = u.user_id
                LEFT JOIN Cabs c ON d.driver_id = c.driver_id
                WHERE d.user_id = ?
            """, (user_id,))
            driver = cursor.fetchone()
            
            if not driver:
                return error_response("User is not a driver", 403)
            
            profile = {
                "driver_id": driver[0],
                "name": driver[1],
                "email": driver[2],
                "license_number": driver[3],
                "availability_status": driver[4],
                "vehicle_number": driver[5],
                "vehicle_type": driver[6],
                "rating": float(driver[7]) if driver[7] else 0.0,
                "total_ratings": driver[8] if driver[8] else 0
            }
        
        return success_response("Profile retrieved", {"profile": profile})
    except Exception as e:
        logger.error(f"Get driver profile error: {e}")
        return error_response("Failed to get profile", 500)
