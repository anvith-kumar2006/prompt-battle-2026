from backend.app.extensions import db
from datetime import datetime

class Route(db.Model):
    __tablename__ = 'routes'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120))
    institution_id = db.Column(db.BigInteger, db.ForeignKey('institutions.id'), nullable=True)
    origin_lat = db.Column(db.Numeric(9, 6))
    origin_lng = db.Column(db.Numeric(9, 6))
    dest_lat = db.Column(db.Numeric(9, 6))
    dest_lng = db.Column(db.Numeric(9, 6))
    polyline_json = db.Column(db.JSON, nullable=False)
    distance_m = db.Column(db.Integer)
    is_template = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TransportDisruption(db.Model):
    __tablename__ = 'transport_disruptions'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    route_id = db.Column(db.BigInteger, db.ForeignKey('routes.id'), nullable=True)
    stop_label = db.Column(db.String(120))
    type = db.Column(db.Enum('CANCELLED', 'DELAYED', 'ROUTE_DISRUPTED', 'OVERCROWDED'), nullable=False)
    starts_at = db.Column(db.DateTime, nullable=False)
    ends_at = db.Column(db.DateTime, nullable=True)
    note = db.Column(db.Text)
    reported_by = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    source = db.Column(db.Enum('MANUAL', 'DEMO'), default='MANUAL')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
