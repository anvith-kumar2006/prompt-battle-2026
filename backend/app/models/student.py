from backend.app.extensions import db
from datetime import datetime, date

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    guardian_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    institution_id = db.Column(db.BigInteger, db.ForeignKey('institutions.id'), nullable=False)
    first_name = db.Column(db.String(60), nullable=False)
    class_label = db.Column(db.String(30))
    dob = db.Column(db.Date)
    age_category = db.Column(db.Enum('MINOR_PRIMARY', 'MINOR_SECONDARY', 'ADULT'), nullable=False)
    status = db.Column(db.Enum('ACTIVE', 'INACTIVE', 'ARCHIVED'), default='ACTIVE')
    default_route_id = db.Column(db.BigInteger, db.ForeignKey('routes.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    guardian = db.relationship('User', back_populates='students', foreign_keys=[guardian_id])
    institution = db.relationship('Institution', back_populates='students')
    
    @staticmethod
    def calculate_age_category(dob):
        """Calculate age category from date of birth"""
        if not dob:
            return 'MINOR_SECONDARY'  # Default assumption
        
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        
        if age < 11:
            return 'MINOR_PRIMARY'
        elif age < 18:
            return 'MINOR_SECONDARY'
        else:
            return 'ADULT'
    
    def to_dict(self, include_guardian=False):
        data = {
            'id': self.id,
            'first_name': self.first_name,
            'class_label': self.class_label,
            'dob': self.dob.isoformat() if self.dob else None,
            'age_category': self.age_category,
            'status': self.status,
            'institution_id': self.institution_id,
            'institution_name': self.institution.name if self.institution else None
        }
        if include_guardian:
            data['guardian_id'] = self.guardian_id
        return data
