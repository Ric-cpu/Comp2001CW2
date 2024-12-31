from config import app, db
from models import Trail, LocationPoint

TRAILS = [
    {"TrailName": "Trail 1"},
    {"TrailName": "Trail 2"}
]

LOCATION_POINTS = [
    {"Latitude": 50.123, "Longitude": -4.123, "Order": 1, "TrailID": 1},
    {"Latitude": 50.124, "Longitude": -4.124, "Order": 2, "TrailID": 1}
]

with app.app_context():
    db.drop_all()
    db.create_all()

    for trail in TRAILS:
        db.session.add(Trail(**trail))

    for point in LOCATION_POINTS:
        db.session.add(LocationPoint(**point))

    db.session.commit()
