import jwt
import requests
from flask import Flask, render_template, jsonify, request, abort
from flask_swagger_ui import get_swaggerui_blueprint
from datetime import datetime, timedelta
import config
from models import Trail, LocationPoint, db
import notes  

# Constants
SECRET_KEY = "secret-key"
AUTH_URL = "https://web.socem.plymouth.ac.uk/COMP2001/auth/api/users"
TOKEN_EXPIRATION_MINUTES = 60

# Initialize Connexion app and Flask app
app = config.connex_app
flask_app = app.app

# Swagger UI Configuration
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.yml'
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
flask_app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Helper Functions for JWT

def generate_jwt(user_data):
    """
    Generate a JWT token for the authenticated user.
    """
    payload = {
        "email": user_data["email"],
        "role": user_data.get("role", "User"),  # Default role to "User"
        "exp": datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRATION_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def validate_token(token):
    """
    Validate and decode the JWT token.
    """
    try:
        token = token.split(" ")[1] if " " in token else token
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        abort(401, description="Token has expired")
    except jwt.InvalidTokenError:
        abort(401, description="Invalid token")

def require_auth(roles=None):
    """
    Decorator to enforce JWT authentication and role-based access control.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            token = request.headers.get("Authorization")
            if not token:
                abort(401, description="Authorization token is missing")
            
            decoded = validate_token(token)
            user_role = decoded.get("role")
            if roles and user_role not in roles:
                abort(403, description="Forbidden: Insufficient permissions")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Routes

@flask_app.route("/login", methods=["POST"])
def login():
    """
    Authenticate the user and generate a JWT token.
    """
    data = request.json
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return {"error": "Email and password are required"}, 400

    # Authenticate with the external API
    response = requests.post(AUTH_URL, json={"email": email, "password": password})
    if response.status_code != 200:
        abort(401, description="Invalid credentials")

    user_data = response.json()
    token = generate_jwt(user_data)
    return jsonify({"token": token}), 200

@flask_app.route("/trails", methods=["POST"])
@require_auth(roles=["Admin"])
def create_trail():
    """
    Create a new trail (Admin only).
    """
    trail_data = request.json
    if not trail_data:
        abort(400, description="Request body is missing")
    return jsonify(notes.create_trail(trail_data)), 201

@flask_app.route("/trails", methods=["GET"])
@require_auth()
def read_all_trails():
    """
    Retrieve all trails (All users).
    """
    trails = notes.read_all_trails()
    return jsonify(trails), 200

@flask_app.route("/trails/<int:trail_id>", methods=["GET"])
@require_auth()
def read_one_trail(trail_id):
    """
    Retrieve a specific trail by ID (All users).
    """
    trail = notes.read_one_trail(trail_id)
    return jsonify(trail), 200

@flask_app.route("/trails/<int:trail_id>", methods=["PUT"])
@require_auth(roles=["Admin"])
def update_trail(trail_id):
    """
    Update an existing trail (Admin only).
    """
    trail_data = request.json
    if not trail_data:
        abort(400, description="Request body is missing")
    return jsonify(notes.update_trail(trail_id, trail_data)), 200

@flask_app.route("/trails/<int:trail_id>", methods=["DELETE"])
@require_auth(roles=["Admin"])
def delete_trail(trail_id):
    """
    Delete a trail (Admin only).
    """
    return notes.delete_trail(trail_id), 200

@flask_app.route("/trails/<int:trail_id>/points", methods=["POST"])
@require_auth(roles=["Admin"])
def add_location_point(trail_id):
    """
    Add a location point to a trail (Admin only).
    """
    point_data = request.json
    if not point_data:
        abort(400, description="Request body is missing")
    return jsonify(notes.add_location_point(trail_id, point_data)), 201

@flask_app.route("/trails/<int:trail_id>/points", methods=["GET"])
@require_auth()
def get_location_points(trail_id):
    """
    Retrieve location points for a trail (All users).
    """
    points = notes.get_location_points(trail_id)
    return jsonify(points), 200

@flask_app.route("/trails/<int:trail_id>/points/<int:point_id>", methods=["PUT"])
@require_auth(roles=["Admin"])
def update_location_point(trail_id, point_id):
    """
    Update a location point (Admin only).
    """
    point_data = request.json
    if not point_data:
        abort(400, description="Request body is missing")
    return jsonify(notes.update_location_point(trail_id, point_id, point_data)), 200

@flask_app.route("/trails/<int:trail_id>/points/<int:point_id>", methods=["DELETE"])
@require_auth(roles=["Admin"])
def delete_location_point(trail_id, point_id):
    """
    Delete a location point (Admin only).
    """
    return notes.delete_location_point(trail_id, point_id), 200

@flask_app.route("/")
def home():
    """
    Render the home page.
    """
    return render_template("home.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
