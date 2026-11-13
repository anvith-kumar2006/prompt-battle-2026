from backend.app.extensions import db
from datetime import datetime

class LocationUpdate(db.Model):
    __tablename__ = 'location_updates'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    trip_id = db.Column(db.BigInteger, db.ForeignKey('trips.id'), nullable=False)
    driver_id = db.Column(db.BigInteger, db.ForeignKey('drivers.id'), nullable=False)
    lat = db.Column(db.Numeric(9, 6), nullable=False)
    lng = db.Column(db.Numeric(9, 6), nullable=False)
    accuracy_m = db.Column(db.Float)
    speed_mps = db.Column(db.Float, nullable=True)
    heading = db.Column(db.Float, nullable=True)
    client_ts = db.Column(db.DateTime(3))
    server_ts = db.Column(db.DateTime(3), nullable=False, default=datetime.utcnow)
    dist_from_route_m = db.Column(db.Float, nullable=True)
    in_corridor = db.Column(db.Boolean, nullable=True)
    flags = db.Column(db.String(100), nullable=True)  # SET type emulated
    is_simulated = db.Column(db.Boolean, default=False)
    
    # Relationships
    trip = db.relationship('Trip', back_populates='location_updates')
    
    def to_dict(self):
        return {
            'id': self.id,
            'trip_id': self.trip_id,
            'lat': float(self.lat),
            'lng': float(self.lng),
            'accuracy_m': self.accuracy_m,
            'speed_mps': self.speed_mps,
            'heading': self.heading,
            'server_ts': self.server_ts.isoformat(),
            'in_corridor': self.in_corridor,
            'is_simulated': self.is_simulated
        }

class JourneyEvent(db.Model):
    __tablename__ = 'journey_events'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    trip_id = db.Column(db.BigInteger, db.ForeignKey('trips.id'), nullable=False)
    event_type = db.Column(db.String(40), nullable=False)
    severity = db.Column(db.Enum('INFO', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'), default='INFO')
    payload_json = db.Column(db.JSON)
    actor_user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    trip = db.relationship('Trip', back_populates='events')
    
    def to_dict(self):
        return {
            'event_type': self.event_type,
            'severity': self.severity,
            'payload': self.payload_json,
            'created_at': self.created_at.isoformat()
        }

class Incident(db.Model):
    __tablename__ = 'incidents'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    trip_id = db.Column(db.BigInteger, db.ForeignKey('trips.id'), nullable=False)
    severity = db.Column(db.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'), nullable=False)
    status = db.Column(db.Enum('OPEN', 'ACKNOWLEDGED', 'ESCALATED', 'RESOLVED'), default='OPEN')
    cause_hint = db.Column(db.Enum('GPS_ERROR_SUSPECTED', 'SIGNAL_LOSS', 'TRAFFIC_DIVERSION', 'ROAD_CLOSURE', 'UNEXPLAINED_PERSISTENT_DEVIATION', 'EMERGENCY_REPORTED', 'OTHER'), default='UNEXPLAINED_PERSISTENT_DEVIATION')
    source = db.Column(db.Enum('ENGINE', 'DRIVER_SOS', 'GUARDIAN_CONCERN', 'ADMIN'), default='ENGINE')
    last_lat = db.Column(db.Numeric(9, 6))
    last_lng = db.Column(db.Numeric(9, 6))
    last_seen_at = db.Column(db.DateTime)
    driver_reason = db.Column(db.String(40), nullable=True)
    opened_at = db.Column(db.DateTime, default=datetime.utcnow)
    acknowledged_by = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=True)
    acknowledged_at = db.Column(db.DateTime, nullable=True)
    escalation_note = db.Column(db.Text, nullable=True)
    escalated_at = db.Column(db.DateTime, nullable=True)
    resolved_by = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    resolution_type = db.Column(db.Enum('FALSE_ALARM', 'TRAFFIC_OR_ROAD', 'DRIVER_EXPLAINED', 'SAFETY_CONCERN_CONFIRMED', 'EMERGENCY_HANDLED'), nullable=True)
    resolution_notes = db.Column(db.Text)
    
    # Relationships
    trip = db.relationship('Trip', back_populates='incidents')
    
    def to_dict(self):
        return {
            'id': self.id,
            'trip_id': self.trip_id,
            'severity': self.severity,
            'status': self.status,
            'cause_hint': self.cause_hint,
            'source': self.source,
            'last_location': {'lat': float(self.last_lat), 'lng': float(self.last_lng)} if self.last_lat else None,
            'last_seen_at': self.last_seen_at.isoformat() if self.last_seen_at else None,
            'opened_at': self.opened_at.isoformat(),
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolution_type': self.resolution_type
        }
