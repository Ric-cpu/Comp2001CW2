from flask import Flask, render_template, jsonify, request, abort
from flask_swagger_ui import get_swaggerui_blueprint
import jwt
import datetime
import functools
import config
from models import Trail
import notes  # Your module with business logic

SECRET_KEY = "your-secret-key"

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
        return {"error": "Email and password are required"}, 400

    if email == "grace@plymouth.ac.uk" and password == "ISAD123!":
        user_data = {"user_id": "1", "email": email, "role": "Admin"}
    elif email == "tim@plymouth.ac.uk" and password == "COMP2001!":
        user_data = {"user_id": "2", "email": email, "role": "User"}
    elif email == "ada@plymouth.ac.uk" and password == "insecurePassword":
        user_data = {"user_id": "3", "email": email, "role": "User"}
    else:
        abort(401, description="Invalid credentials")

    token = generate_jwt(user_data)
    return jsonify({"token": token}), 200

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
