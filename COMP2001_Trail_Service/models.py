import pytz
from datetime import datetime
from marshmallow_sqlalchemy import fields
from config import db, ma

# User table
class User(db.Model):
    __tablename__ = "User"
    __table_args__ = {'schema': 'CW2'}
    UserID = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(255), nullable=False, unique=True)
    Email = db.Column(db.String(255), nullable=False, unique=True)
    Password = db.Column(db.String(255), nullable=False)
    Role = db.Column(db.String(50), nullable=False)  # e.g., Admin or User

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        sqla_session = db.session

# Feature table
class Feature(db.Model):
    __tablename__ = "FEATURE"
    __table_args__ = {'schema': 'CW2'}
    TrailFeatureID = db.Column(db.Integer, primary_key=True)
    TrailFeature = db.Column(db.String(255), nullable=False, unique=True)

class FeatureSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Feature
        load_instance = True
        sqla_session = db.session

# Trail table
class Trail(db.Model):
    __tablename__ = "TRAIL"
    __table_args__ = {'schema': 'CW2'}
    TrailID = db.Column(db.Integer, primary_key=True)
    TrailName = db.Column(db.String(255), nullable=False, unique=True)
    TrailSummary = db.Column(db.Text, nullable=False)
    TrailDescription = db.Column(db.Text, nullable=False)
    Difficulty = db.Column(db.String(50), nullable=False)
    Location = db.Column(db.String(255), nullable=False)
    Length = db.Column(db.Float, nullable=False)
    ElevationGain = db.Column(db.Float, nullable=False)
    RouteType = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(
        db.DateTime,
        default=lambda: datetime.now(pytz.timezone('Europe/London')),
        onupdate=lambda: datetime.now(pytz.timezone('Europe/London'))
    )
    
    
    location_points = db.relationship(
        "LocationPoint",
        back_populates="trail",
        cascade="all, delete-orphan"
    )
    
    # LocationPoint table
class LocationPoint(db.Model):
    __tablename__ = "LocationPoint"
    __table_args__ = {'schema': 'CW2'}
    LocationPointID = db.Column(db.Integer, primary_key=True)
    TrailID = db.Column(db.Integer, db.ForeignKey("CW2.TRAIL.TrailID"), nullable=False)
    Latitude = db.Column(db.Float, nullable=False)
    Longitude = db.Column(db.Float, nullable=False)
    Order = db.Column(db.Integer, nullable=False)

    trail = db.relationship("Trail", back_populates="location_points")

class TrailSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Trail
        load_instance = True
        sqla_session = db.session

    location_points = ma.Nested("LocationPointSchema", many=True)


# Many-to-Many relationship table
class TrailFeature(db.Model):
    __tablename__ = "TRAIL_FEATURE"
    __table_args__ = {'schema': 'CW2'}
    TrailID = db.Column(db.Integer, db.ForeignKey("CW2.TRAIL.TrailID"), primary_key=True)
    TrailFeatureID = db.Column(db.Integer, db.ForeignKey("CW2.FEATURE.TrailFeatureID"), primary_key=True)

class TrailFeatureSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TrailFeature
        load_instance = True
        sqla_session = db.session
        include_fk = True

# Log table
class TrailLog(db.Model):
    __tablename__ = "Trail_Log"
    __table_args__ = {'schema': 'CW2'}
    LogID = db.Column(db.Integer, primary_key=True)
    TrailID = db.Column(db.Integer, db.ForeignKey("CW2.TRAIL.TrailID"))
    UserID = db.Column(db.Integer, db.ForeignKey("CW2.User.UserID"))  # Link to User table
    AddedBy = db.Column(db.String(50), nullable=False)
    Timestamp = db.Column(
        db.DateTime, default=lambda: datetime.now(pytz.timezone('Europe/London'))
    )

class TrailLogSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TrailLog
        load_instance = True
        sqla_session = db.session
        include_fk = True
        
        
        
class LocationPointSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LocationPoint
        load_instance = True
        sqla_session = db.session
        include_fk = True

    TrailID = ma.auto_field(required=False)  # Make TrailID optional for the schema


# Marshmallow schemas
user_schema = UserSchema()
users_schema = UserSchema(many=True)

feature_schema = FeatureSchema()
features_schema = FeatureSchema(many=True)

trail_schema = TrailSchema()
trails_schema = TrailSchema(many=True)

trail_feature_schema = TrailFeatureSchema()
trail_features_schema = TrailFeatureSchema(many=True)

trail_log_schema = TrailLogSchema()
trail_logs_schema = TrailLogSchema(many=True)

location_point_schema = LocationPointSchema()
location_points_schema = LocationPointSchema(many=True)