from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from app.middlewares.auth_middleware import role_required
from app.services.driver_service import (
    update_status, get_driver_rides, get_driver_earnings,
    get_available_drivers, get_driver_profile
)

driver_bp = Blueprint("drivers", __name__)

@driver_bp.route("/status", methods=["PATCH"])
@role_required("DRIVER")
def status():
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
    user_id = get_jwt_identity()
    driver_status = request.json.get('status', '').upper()
    return update_status(user_id, driver_status)

@driver_bp.route("/rides", methods=["GET"])
@role_required("DRIVER")
def rides():
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
    user_id = get_jwt_identity()
    return get_driver_rides(user_id)

@driver_bp.route("/earnings", methods=["GET"])
@role_required("DRIVER")
def earnings():
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
    user_id = get_jwt_identity()
    return get_driver_earnings(user_id)

@driver_bp.route("/available", methods=["GET"])
def available():
    """
    Get available drivers
    ---
    tags:
      - Drivers
    responses:
      200:
        description: Available drivers retrieved
    """
    return get_available_drivers()

@driver_bp.route("/profile", methods=["GET"])
@role_required("DRIVER")
def profile():
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
    user_id = get_jwt_identity()
    return get_driver_profile(user_id)
