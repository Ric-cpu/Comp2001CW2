from flask import abort, make_response, request
from config import db
from models import Trail, Feature, LocationPoint, TrailLog, trail_schema, trails_schema, feature_schema, features_schema, trail_logs_schema, location_point_schema, location_points_schema
import jwt

# Secret key for JWT validation
SECRET_KEY = "secret-key"

# Token validation function
def validate_token(token):
    try:
        # Remove "Bearer " prefix if present
        token = token.split(" ")[1] if " " in token else token
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded_token  # Return decoded token if needed
    except jwt.ExpiredSignatureError:
        abort(401, description="Token has expired")
    except jwt.InvalidTokenError:
        abort(401, description="Invalid token")

# Authentication decorator with role-based access
def require_auth(roles=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            token = request.headers.get("Authorization")
            if not token:
                abort(401, description="Authorization token is missing")
            decoded = validate_token(token)
            if roles and decoded.get("role") not in roles:
                abort(403, description="Forbidden: Insufficient permissions")
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Trail Functions
@require_auth(roles=["Admin", "User"])  # Both Admin and User can read trails
def read_all_trails():
    trails = Trail.query.all()
    if trails:
        return trails_schema.dump(trails), 200
    abort(404, description="No trails found")

@require_auth(roles=["Admin"])  # Only Admin can create trails
def create_trail(trail):
    trail_name = trail.get("TrailName")
    existing_trail = Trail.query.filter(Trail.TrailName == trail_name).one_or_none()

    if not existing_trail:
        new_trail = trail_schema.load(trail, session=db.session)
        db.session.add(new_trail)
        db.session.commit()
        return trail_schema.dump(new_trail), 201
    abort(406, description=f"Trail with name {trail_name} already exists")

@require_auth(roles=["Admin", "User"])  # Both Admin and User can read a single trail
def read_one_trail(trail_id):
    trail = Trail.query.get(trail_id)
    if trail:
        return trail_schema.dump(trail)
    abort(404, description=f"Trail with ID {trail_id} not found")

@require_auth(roles=["Admin"])  # Only Admin can update trails
def update_trail(trail_id, trail):
    existing_trail = Trail.query.get(trail_id)
    if existing_trail:
        for key, value in trail.items():
            setattr(existing_trail, key, value)
        db.session.commit()
        return trail_schema.dump(existing_trail), 200
    abort(404, description=f"Trail with ID {trail_id} not found")

@require_auth(roles=["Admin"])  # Only Admin can delete trails
def delete_trail(trail_id):
    existing_trail = Trail.query.get(trail_id)
    if existing_trail:
        db.session.delete(existing_trail)
        db.session.commit()
        return {"message": f"Trail ID {trail_id} successfully deleted"}, 200
    abort(404, description=f"Trail with ID {trail_id} not found")

# Location Point Functions
@require_auth(roles=["Admin", "User"])  # Both Admin and User can add location points
def add_location_point(trail_id, location_data):
    trail = Trail.query.get(trail_id)
    if not trail:
        abort(404, description=f"Trail with ID {trail_id} not found")
    try:
        location_point = location_point_schema.load(location_data, session=db.session)
        location_point.TrailID = trail_id
        db.session.add(location_point)
        db.session.commit()
        return location_point_schema.dump(location_point), 201
    except Exception as e:
        abort(400, description=str(e))

@require_auth(roles=["Admin", "User"])  # Both Admin and User can get location points
def get_location_points(trail_id):
    trail = Trail.query.get(trail_id)
    if not trail:
        abort(404, description=f"Trail with ID {trail_id} not found")
    return location_points_schema.dump(trail.location_points), 200

@require_auth(roles=["Admin"])  # Only Admin can update location points
def update_location_point(trail_id, point_id, location_data):
    location_point = LocationPoint.query.filter_by(LocationPointID=point_id, TrailID=trail_id).first()
    if not location_point:
        abort(404, description=f"Location point with ID {point_id} not found on trail ID {trail_id}")
    try:
        for key, value in location_data.items():
            setattr(location_point, key, value)
        db.session.commit()
        return location_point_schema.dump(location_point), 200
    except Exception as e:
        abort(400, description=str(e))

@require_auth(roles=["Admin"])  # Only Admin can delete location points
def delete_location_point(trail_id, point_id):
    location_point = LocationPoint.query.filter_by(LocationPointID=point_id, TrailID=trail_id).first()
    if not location_point:
        abort(404, description=f"Location point with ID {point_id} not found on trail ID {trail_id}")
    db.session.delete(location_point)
    db.session.commit()
    return {"message": f"Location point ID {point_id} successfully deleted from trail ID {trail_id}"}, 200

# Trail Log Functions
@require_auth(roles=["Admin", "User"])  # Both Admin and User can read trail logs
def read_all_trail_logs():
    logs = TrailLog.query.all()
    if logs:
        return trail_logs_schema.dump(logs), 200
    abort(404, description="No trail logs found")
