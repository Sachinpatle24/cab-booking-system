from flask import Blueprint, request
from app.services.auth_service import register_user, login_user

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - email
            - password
          properties:
            name:
              type: string
              example: John Doe
            email:
              type: string
              example: john@example.com
            password:
              type: string
              example: securepass123
            role:
              type: string
              enum: [PASSENGER, DRIVER, ADMIN]
              default: PASSENGER
              example: PASSENGER
    responses:
      201:
        description: User registered successfully
      400:
        description: Validation error
      409:
        description: Email already registered
    """
    data = request.get_json()
    return register_user(data)

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    User login
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: john@example.com
            password:
              type: string
              example: securepass123
    responses:
      200:
        description: Login successful
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
                access_token:
                  type: string
                user:
                  type: object
      401:
        description: Invalid credentials
    """
    data = request.get_json()
    return login_user(data)
