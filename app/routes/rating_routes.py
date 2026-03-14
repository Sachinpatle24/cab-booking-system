from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.rating_service import rate_ride, get_ride_rating

rating_bp = Blueprint("ratings", __name__)

@rating_bp.route("/ride/<int:ride_id>", methods=["POST"])
@jwt_required()
def submit_rating(ride_id):
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
    return rate_ride(user_id, ride_id, data)

@rating_bp.route("/ride/<int:ride_id>", methods=["GET"])
@jwt_required()
def ride_rating(ride_id):
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
    return get_ride_rating(ride_id)
