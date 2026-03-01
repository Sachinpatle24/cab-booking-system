from app.database.db_connection import get_db_cursor
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

def update_eco_score(user_id, points):
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                "UPDATE Users SET eco_score = eco_score + ? WHERE user_id = ?",
                (points, user_id)
            )
        logger.info(f"Eco score updated for user {user_id}: +{points}")
    except Exception as e:
        logger.error(f"Update eco score error: {e}")

def calculate_eco_points(distance, eco_mode, is_electric):
    points = 0
    if eco_mode:
        points += int(distance * 2)
    if is_electric:
        points += int(distance * 3)
    return points
