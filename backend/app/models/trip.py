from backend.app.extensions import db
from datetime import datetime

class Trip(db.Model):
    __tablename__ = 'trips'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    allocation_id = db.Column(db.BigInteger, db.ForeignKey('allocations.id'), unique=True, nullable=False)
    vehicle_id = db.Column(db.BigInteger, db.ForeignKey('vehicles.id'), nullable=False)
    driver_id = db.Column(db.BigInteger, db.ForeignKey('drivers.id'), nullable=False)
    status = db.Column(db.Enum('SCHEDULED', 'EN_ROUTE_TO_PICKUP', 'AT_PICKUP', 'IN_PROGRESS', 'ARRIVED', 'COMPLETED', 'CANCELLED', 'ABORTED'), default='SCHEDULED')
    planned_pickup_at = db.Column(db.DateTime, nullable=False)
    pickup_lat = db.Column(db.Numeric(9, 6), nullable=False)
    pickup_lng = db.Column(db.Numeric(9, 6), nullable=False)
    dest_lat = db.Column(db.Numeric(9, 6), nullable=False)
    dest_lng = db.Column(db.Numeric(9, 6), nullable=False)
    destination_institution_id = db.Column(db.BigInteger, db.ForeignKey('institutions.id'), nullable=True)
    route_polyline_json = db.Column(db.JSON)
    corridor_radius_m = db.Column(db.Integer, default=500)
    deviation_state = db.Column(db.JSON, nullable=True)
    pickup_at = db.Column(db.DateTime, nullable=True)
    pickup_actual_lat = db.Column(db.Numeric(9, 6), nullable=True)
    pickup_actual_lng = db.Column(db.Numeric(9, 6), nullable=True)
    dropoff_at = db.Column(db.DateTime, nullable=True)
    dropoff_actual_lat = db.Column(db.Numeric(9, 6), nullable=True)
    dropoff_actual_lng = db.Column(db.Numeric(9, 6), nullable=True)
    handover_method = db.Column(db.Enum('OTP', 'STAFF_CONFIRM', 'ADMIN_OVERRIDE'), nullable=True)
    handover_by = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=True)
    last_ping_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    allocation = db.relationship('Allocation', back_populates='trip')
    passengers = db.relationship('TripPassenger', back_populates='trip')
    location_updates = db.relationship('LocationUpdate', back_populates='trip')
    otp_challenges = db.relationship('OTPChallenge', back_populates='trip')
    events = db.relationship('JourneyEvent', back_populates='trip')
    incidents = db.relationship('Incident', back_populates='trip')
    
    def is_trackable(self):
        """Check if GPS tracking is active for this trip"""
        return self.status in ['EN_ROUTE_TO_PICKUP', 'AT_PICKUP', 'IN_PROGRESS', 'ARRIVED']
    
    def to_dict(self, include_passengers=False):
        data = {
            'id': self.id,
            'status': self.status,
            'planned_pickup_at': self.planned_pickup_at.isoformat(),
            'pickup': {'lat': float(self.pickup_lat), 'lng': float(self.pickup_lng)},
            'destination': {'lat': float(self.dest_lat), 'lng': float(self.dest_lng)},
            'pickup_at': self.pickup_at.isoformat() if self.pickup_at else None,
            'dropoff_at': self.dropoff_at.isoformat() if self.dropoff_at else None,
            'last_ping_at': self.last_ping_at.isoformat() if self.last_ping_at else None,
            'created_at': self.created_at.isoformat()
        }
        if include_passengers:
            data['passengers'] = [p.student.to_dict() for p in self.passengers]
        return data

class TripPassenger(db.Model):
    __tablename__ = 'trip_passengers'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    trip_id = db.Column(db.BigInteger, db.ForeignKey('trips.id'), nullable=False)
    student_id = db.Column(db.BigInteger, db.ForeignKey('students.id'), nullable=False)
    pickup_confirmed_at = db.Column(db.DateTime, nullable=True)
    dropoff_confirmed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    trip = db.relationship('Trip', back_populates='passengers')
    student = db.relationship('Student')
    
    __table_args__ = (db.UniqueConstraint('trip_id', 'student_id', name='unique_trip_student'),)

class OTPChallenge(db.Model):
    __tablename__ = 'otp_challenges'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    trip_id = db.Column(db.BigInteger, db.ForeignKey('trips.id'), nullable=False)
    purpose = db.Column(db.Enum('PICKUP', 'DROPOFF'), nullable=False)
    code_hash = db.Column(db.String(64), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    attempts = db.Column(db.SmallInteger, default=0)
    max_attempts = db.Column(db.SmallInteger, default=5)
    status = db.Column(db.Enum('ACTIVE', 'CONSUMED', 'EXPIRED', 'LOCKED', 'SUPERSEDED'), default='ACTIVE')
    consumed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    trip = db.relationship('Trip', back_populates='otp_challenges')
    
    def to_dict(self, include_hash=False):
        data = {
            'id': self.id,
            'trip_id': self.trip_id,
            'purpose': self.purpose,
            'expires_at': self.expires_at.isoformat(),
            'attempts': self.attempts,
            'max_attempts': self.max_attempts,
            'status': self.status
        }
        if include_hash:
            data['code_hash'] = self.code_hash
        return data
