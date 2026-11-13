from backend.app.extensions import db
from datetime import datetime, date

class Driver(db.Model):
    __tablename__ = 'drivers'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), unique=True, nullable=False)
    category = db.Column(db.Enum('SCHOOL_APPROVED', 'COMMUNITY'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    licence_no = db.Column(db.String(32), unique=True, nullable=False)
    licence_class = db.Column(db.String(20))
    licence_expiry = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('PENDING', 'APPROVED', 'REJECTED', 'SUSPENDED'), default='PENDING')
    availability = db.Column(db.Enum('AVAILABLE', 'UNAVAILABLE'), default='UNAVAILABLE')
    verification_notes = db.Column(db.Text)
    verified_by = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=True)
    verified_at = db.Column(db.DateTime, nullable=True)
    is_simulated_verification = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='driver', foreign_keys=[user_id])
    vehicles = db.relationship('Vehicle', back_populates='driver')
    
    def is_eligible(self, travel_date=None):
        """Check if driver is eligible for matching"""
        if self.status != 'APPROVED':
            return False
        if self.availability != 'AVAILABLE':
            return False
        check_date = travel_date or date.today()
        if self.licence_expiry < check_date:
            return False
        return True
    
    def to_dict(self, mask_sensitive=True):
        return {
            'id': self.id,
            'category': self.category,
            'full_name': self.full_name if not mask_sensitive else self.full_name.split()[0],
            'licence_no': self.licence_no if not mask_sensitive else f"{self.licence_no[:4]}****{self.licence_no[-4:]}",
            'licence_expiry': self.licence_expiry.isoformat(),
            'status': self.status,
            'availability': self.availability,
            'is_simulated_verification': self.is_simulated_verification
        }

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    driver_id = db.Column(db.BigInteger, db.ForeignKey('drivers.id'), nullable=False)
    reg_no = db.Column(db.String(16), unique=True, nullable=False)
    type = db.Column(db.Enum('BUS', 'VAN', 'AUTO'), nullable=False)
    permitted_capacity = db.Column(db.SmallInteger, nullable=False)
    permit_expiry = db.Column(db.Date)
    insurance_expiry = db.Column(db.Date)
    fitness_expiry = db.Column(db.Date)
    base_lat = db.Column(db.Numeric(9, 6))
    base_lng = db.Column(db.Numeric(9, 6))
    service_radius_km = db.Column(db.Numeric(5, 2), default=10.00)
    status = db.Column(db.Enum('PENDING', 'APPROVED', 'REJECTED', 'SUSPENDED'), default='PENDING')
    verified_by = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=True)
    verified_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    driver = db.relationship('Driver', back_populates='vehicles')
    
    def is_eligible(self, travel_date=None):
        """Check if vehicle is eligible for matching"""
        if self.status != 'APPROVED':
            return False
        check_date = travel_date or date.today()
        if self.permit_expiry and self.permit_expiry < check_date:
            return False
        if self.insurance_expiry and self.insurance_expiry < check_date:
            return False
        if self.fitness_expiry and self.fitness_expiry < check_date:
            return False
        return True
    
    def to_dict(self, mask_sensitive=True):
        return {
            'id': self.id,
            'reg_no': f"{self.reg_no[:4]}••••{self.reg_no[-4:]}" if mask_sensitive else self.reg_no,
            'type': self.type,
            'permitted_capacity': self.permitted_capacity,
            'permit_expiry': self.permit_expiry.isoformat() if self.permit_expiry else None,
            'insurance_expiry': self.insurance_expiry.isoformat() if self.insurance_expiry else None,
            'fitness_expiry': self.fitness_expiry.isoformat() if self.fitness_expiry else None,
            'base_lat': float(self.base_lat) if self.base_lat else None,
            'base_lng': float(self.base_lng) if self.base_lng else None,
            'service_radius_km': float(self.service_radius_km) if self.service_radius_km else None,
            'status': self.status
        }

class ProviderDocument(db.Model):
    __tablename__ = 'provider_documents'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    owner_type = db.Column(db.Enum('DRIVER', 'VEHICLE'), nullable=False)
    owner_id = db.Column(db.BigInteger, nullable=False)
    doc_type = db.Column(db.Enum('LICENCE', 'RC', 'INSURANCE', 'PERMIT', 'FITNESS', 'POLICE_CLEARANCE'), nullable=False)
    doc_number = db.Column(db.String(50))
    expiry_date = db.Column(db.Date, nullable=True)
    file_path = db.Column(db.String(255), nullable=True)
    status = db.Column(db.Enum('SUBMITTED', 'ACCEPTED', 'REJECTED'), default='SUBMITTED')
    reviewed_by = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
