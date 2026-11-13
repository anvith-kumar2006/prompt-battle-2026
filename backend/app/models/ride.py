from backend.app.extensions import db
from datetime import datetime

class RideRequest(db.Model):
    __tablename__ = 'ride_requests'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    guardian_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    institution_id = db.Column(db.BigInteger, db.ForeignKey('institutions.id'))
    pickup_lat = db.Column(db.Numeric(9, 6), nullable=False)
    pickup_lng = db.Column(db.Numeric(9, 6), nullable=False)
    pickup_label = db.Column(db.String(200))
    dest_lat = db.Column(db.Numeric(9, 6), nullable=False)
    dest_lng = db.Column(db.Numeric(9, 6), nullable=False)
    dest_label = db.Column(db.String(200))
    travel_date = db.Column(db.Date, nullable=False)
    pickup_time = db.Column(db.Time, nullable=False)
    shared_ok = db.Column(db.Boolean, default=False)
    disruption_id = db.Column(db.BigInteger, db.ForeignKey('transport_disruptions.id'), nullable=True)
    status = db.Column(db.Enum('SUBMITTED', 'NO_MATCH', 'PROPOSED', 'CONFIRMED', 'REJECTED_BY_PARENT', 'EXPIRED', 'CANCELLED', 'COMPLETED'), default='SUBMITTED')
    expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    students = db.relationship('Student', secondary='ride_request_students', backref='ride_requests')
    allocations = db.relationship('Allocation', back_populates='request')
    
    def to_dict(self, include_students=False):
        data = {
            'id': self.id,
            'guardian_id': self.guardian_id,
            'pickup': {'lat': float(self.pickup_lat), 'lng': float(self.pickup_lng), 'label': self.pickup_label},
            'destination': {'lat': float(self.dest_lat), 'lng': float(self.dest_lng), 'label': self.dest_label},
            'travel_date': self.travel_date.isoformat(),
            'pickup_time': self.pickup_time.isoformat(),
            'shared_ok': self.shared_ok,
            'status': self.status,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat()
        }
        if include_students:
            data['students'] = [s.to_dict() for s in self.students]
        return data

class RideRequestStudent(db.Model):
    __tablename__ = 'ride_request_students'
    
    request_id = db.Column(db.BigInteger, db.ForeignKey('ride_requests.id'), primary_key=True)
    student_id = db.Column(db.BigInteger, db.ForeignKey('students.id'), primary_key=True)

class Allocation(db.Model):
    __tablename__ = 'allocations'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    request_id = db.Column(db.BigInteger, db.ForeignKey('ride_requests.id'), nullable=False)
    vehicle_id = db.Column(db.BigInteger, db.ForeignKey('vehicles.id'), nullable=False)
    driver_id = db.Column(db.BigInteger, db.ForeignKey('drivers.id'), nullable=False)
    seats_reserved = db.Column(db.SmallInteger, nullable=False)
    score = db.Column(db.Numeric(6, 3))
    window_start = db.Column(db.DateTime)
    window_end = db.Column(db.DateTime)
    status = db.Column(db.Enum('PROPOSED', 'CONFIRMED', 'RELEASED', 'EXPIRED'), default='PROPOSED')
    hold_expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    request = db.relationship('RideRequest', back_populates='allocations')
    vehicle = db.relationship('Vehicle')
    driver = db.relationship('Driver')
    consent = db.relationship('GuardianConsent', back_populates='allocation', uselist=False)
    trip = db.relationship('Trip', back_populates='allocation', uselist=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'request_id': self.request_id,
            'vehicle_id': self.vehicle_id,
            'driver_id': self.driver_id,
            'seats_reserved': self.seats_reserved,
            'score': float(self.score) if self.score else None,
            'status': self.status,
            'hold_expires_at': self.hold_expires_at.isoformat() if self.hold_expires_at else None,
            'driver': self.driver.to_dict(mask_sensitive=True) if self.driver else None,
            'vehicle': self.vehicle.to_dict(mask_sensitive=True) if self.vehicle else None
        }

class GuardianConsent(db.Model):
    __tablename__ = 'guardian_consents'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    allocation_id = db.Column(db.BigInteger, db.ForeignKey('allocations.id'), unique=True, nullable=False)
    guardian_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Enum('PENDING', 'APPROVED', 'REJECTED', 'EXPIRED'), default='PENDING')
    consent_text_version = db.Column(db.String(16), default='v1')
    decided_at = db.Column(db.DateTime, nullable=True)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    allocation = db.relationship('Allocation', back_populates='consent')
    
    def to_dict(self):
        return {
            'id': self.id,
            'allocation_id': self.allocation_id,
            'status': self.status,
            'consent_text_version': self.consent_text_version,
            'decided_at': self.decided_at.isoformat() if self.decided_at else None,
            'created_at': self.created_at.isoformat()
        }
