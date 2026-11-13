from backend.app.extensions import db
from datetime import datetime

class Institution(db.Model):
    __tablename__ = 'institutions'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.Enum('SCHOOL', 'PU', 'COLLEGE'), nullable=False)
    address = db.Column(db.Text)
    lat = db.Column(db.Numeric(9, 6))
    lng = db.Column(db.Numeric(9, 6))
    contact_phone = db.Column(db.String(16))
    status = db.Column(db.Enum('PENDING', 'VERIFIED', 'SUSPENDED'), default='PENDING')
    allows_adult_self_booking = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    students = db.relationship('Student', back_populates='institution')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'address': self.address,
            'lat': float(self.lat) if self.lat else None,
            'lng': float(self.lng) if self.lng else None,
            'status': self.status
        }
