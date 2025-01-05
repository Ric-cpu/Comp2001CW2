from flask import Flask, render_template, jsonify, request, abort
from flask_swagger_ui import get_swaggerui_blueprint
import jwt
import datetime
import functools
import config
from models import Trail
import notes  
import requests  # Import requests for API communication

SECRET_KEY = "secret-key"
AUTH_URL = "https://web.socem.plymouth.ac.uk/COMP2001/auth/api/users"

# Initialize Connexion app and Flask app
app = config.connex_app
flask_app = app.app

# Swagger UI Configuration
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.yml'
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
flask_app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# JWT Helper Functions
def generate_jwt(user_data):
    payload = {
        "user_id": user_data["user_id"],
        "role": user_data.get("role", "user"),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def validate_token(token):
    try:
        token = token.split(" ")[1]
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        abort(401, description="Token has expired")
    except jwt.InvalidTokenError:
        abort(401, description="Invalid token")

def require_auth(func):
    @functools.wraps(func)  # Preserve the original function's name
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            abort(401, description="Unauthorized")
        validate_token(token)
        return func(*args, **kwargs)
    return wrapper

@flask_app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # Authenticate using external API
    response = requests.post(AUTH_URL, json={"email": email, "password": password})

    if response.status_code != 200:
        print("Authentication Failed:", response.text)
        abort(401, description="Invalid credentials")

    try:
        user_data = response.json()
        print("User Data Received:", user_data)
    except ValueError:
        abort(500, description="Invalid response from authentication server")

    # **NEW FIX: Assign Role Based on Email**
    if isinstance(user_data, list):
        if "Verified" in user_data and "True" in user_data:
            user_id = email  # Use email as the user identifier
            
            # **Manually Define Admin Emails Here**
            admin_users = ["grace@plymouth.ac.uk"]
            role = "Admin" if email in admin_users else "User"
        else:
            abort(500, description=f"Unexpected list response from authentication server: {user_data}")
    elif isinstance(user_data, dict):
        user_id = user_data.get("id") or user_data.get("user_id")
        role = user_data.get("role", "User")  # Default to "User"
    else:
        abort(500, description=f"Unexpected response format from authentication server: {user_data}")

    if not user_id:
        abort(500, description="Missing user ID in authentication response")

    # Generate JWT
    token = generate_jwt({"user_id": user_id, "role": role})
    
    return jsonify({"token": token, "role": role}), 200  # ✅ Include role in response






@flask_app.route("/trails", methods=["POST"])
@require_auth
def create_trail():
    trail_data = request.json
    if not trail_data:
        abort(400, description="Request body is missing")
    return jsonify(notes.create_trail(trail_data)), 201

@flask_app.route("/trails", methods=["GET"])
@require_auth
def read_all_trails():
    trails = Trail.query.all()
    return jsonify(notes.trails_schema.dump(trails)), 200

@flask_app.route("/trails/<int:trail_id>", methods=["GET"])
@require_auth
def read_one_trail(trail_id):
    return jsonify(notes.read_one_trail(trail_id)), 200

@flask_app.route("/trails/<int:trail_id>", methods=["PUT"])
@require_auth
def update_trail(trail_id):
    trail_data = request.json
    if not trail_data:
        abort(400, description="Request body is missing")
    return jsonify(notes.update_trail(trail_id, trail_data)), 200

@flask_app.route("/trails/<int:trail_id>", methods=["DELETE"])
@require_auth
def delete_trail(trail_id):
    result, status_code = notes.delete_trail(trail_id)  # Capture the JSON response and status code
    return jsonify(result), status_code  # Use jsonify to serialize the response

@flask_app.route("/trails/<int:trail_id>/points", methods=["POST"])
@require_auth
def add_point(trail_id):
    data = request.json
    return jsonify(notes.add_location_point(trail_id, data)), 201

@flask_app.route("/trails/<int:trail_id>/points", methods=["GET"])
@require_auth
def get_points(trail_id):
    return jsonify(notes.get_location_points(trail_id)), 200

@flask_app.route("/trails/<int:trail_id>/points/<int:point_id>", methods=["PUT"])
@require_auth
def update_point(trail_id, point_id):
    data = request.json
    return jsonify(notes.update_location_point(trail_id, point_id, data)), 200

@flask_app.route("/trails/<int:trail_id>/points/<int:point_id>", methods=["DELETE"])
@require_auth
def delete_point(trail_id, point_id):
    return jsonify(notes.delete_location_point(trail_id, point_id)), 200

@flask_app.route("/")
def home():
    try:
        trails = Trail.query.all()
        return render_template("home.html", trails=trails)
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

