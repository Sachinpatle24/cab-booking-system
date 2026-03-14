from app.database.db_connection import get_db_cursor
from app.utils.validators import validate_rating
from app.utils.response_handler import success_response, error_response
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

def rate_ride(user_id, ride_id, data):
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

            rating = data.get('rating')
            comment = data.get('comment', '')

            if not validate_rating(rating):
                return error_response("Rating must be an integer between 1 and 5", 400)

            # Passenger rating driver
            if ride[0] == user_id:
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
        logger.error(f"Rate ride error: {e}")
        return error_response("Failed to submit rating", 500)

def get_ride_rating(ride_id):
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
        logger.error(f"Get ride rating error: {e}")
        return error_response("Failed to get rating", 500)
