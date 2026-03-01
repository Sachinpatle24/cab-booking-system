from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database.db_connection import get_db_cursor
from app.utils.response_handler import success_response, error_response

rating_bp = Blueprint("ratings", __name__)

@rating_bp.route("/ride/<int:ride_id>", methods=["POST"])
@jwt_required()
def rate_ride(ride_id):
    """
    Rate a ride
    ---
    tags:
      - Ratings
    security:
      - Bearer: []
    parameters:
      - in: path
        name: ride_id
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            rating:
              type: integer
              minimum: 1
              maximum: 5
            comment:
              type: string
    responses:
      200:
        description: Rating submitted
    """
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT user_id, driver_id, ride_status 
                FROM Rides WHERE ride_id = ?
            """, (ride_id,))
            ride = cursor.fetchone()
            
            if not ride:
                return error_response("Ride not found", 404)
            
            if ride[2] != 'COMPLETED':
                return error_response("Can only rate completed rides", 400)
            
            cursor.execute("SELECT rating_id FROM Ratings WHERE ride_id = ?", (ride_id,))
            existing = cursor.fetchone()
            
            # Passenger rating driver
            if ride[0] == user_id:
                rating = data.get('rating')
                comment = data.get('comment', '')
                
                if not rating or rating < 1 or rating > 5:
                    return error_response("Rating must be between 1 and 5", 400)
                
                if existing:
                    cursor.execute("""
                        UPDATE Ratings 
                        SET passenger_to_driver_rating = ?, passenger_comment = ?
                        WHERE ride_id = ?
                    """, (rating, comment, ride_id))
                else:
                    cursor.execute("""
                        INSERT INTO Ratings (ride_id, passenger_to_driver_rating, passenger_comment)
                        VALUES (?, ?, ?)
                    """, (ride_id, rating, comment))
                
                # Update driver average rating
                if ride[1]:
                    cursor.execute("""
                        UPDATE Drivers 
                        SET rating = (
                            SELECT AVG(CAST(passenger_to_driver_rating AS FLOAT))
                            FROM Ratings r
                            JOIN Rides rd ON r.ride_id = rd.ride_id
                            WHERE rd.driver_id = ? AND passenger_to_driver_rating IS NOT NULL
                        ),
                        total_ratings = (
                            SELECT COUNT(*)
                            FROM Ratings r
                            JOIN Rides rd ON r.ride_id = rd.ride_id
                            WHERE rd.driver_id = ? AND passenger_to_driver_rating IS NOT NULL
                        )
                        WHERE driver_id = ?
                    """, (ride[1], ride[1], ride[1]))
                
                return success_response("Rating submitted successfully")
            
            # Driver rating passenger
            cursor.execute("SELECT driver_id FROM Drivers WHERE user_id = ?", (user_id,))
            driver = cursor.fetchone()
            
            if driver and driver[0] == ride[1]:
                rating = data.get('rating')
                comment = data.get('comment', '')
                
                if not rating or rating < 1 or rating > 5:
                    return error_response("Rating must be between 1 and 5", 400)
                
                if existing:
                    cursor.execute("""
                        UPDATE Ratings 
                        SET driver_to_passenger_rating = ?, driver_comment = ?
                        WHERE ride_id = ?
                    """, (rating, comment, ride_id))
                else:
                    cursor.execute("""
                        INSERT INTO Ratings (ride_id, driver_to_passenger_rating, driver_comment)
                        VALUES (?, ?, ?)
                    """, (ride_id, rating, comment))
                
                return success_response("Rating submitted successfully")
            
            return error_response("You are not part of this ride", 403)
            
    except Exception as e:
        return error_response("Failed to submit rating", 500)

@rating_bp.route("/ride/<int:ride_id>", methods=["GET"])
@jwt_required()
def get_ride_rating(ride_id):
    """
    Get ride rating
    ---
    tags:
      - Ratings
    security:
      - Bearer: []
    parameters:
      - in: path
        name: ride_id
        type: integer
        required: true
    responses:
      200:
        description: Rating retrieved
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT passenger_to_driver_rating, passenger_comment,
                       driver_to_passenger_rating, driver_comment
                FROM Ratings WHERE ride_id = ?
            """, (ride_id,))
            rating = cursor.fetchone()
            
            if not rating:
                return success_response("No ratings yet", {"rated": False})
            
            return success_response("Rating retrieved", {
                "rated": True,
                "passenger_rating": rating[0],
                "passenger_comment": rating[1],
                "driver_rating": rating[2],
                "driver_comment": rating[3]
            })
    except Exception as e:
        return error_response("Failed to get rating", 500)
