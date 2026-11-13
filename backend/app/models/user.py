from backend.app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    role = db.Column(db.Enum('GUARDIAN', 'STUDENT_ADULT', 'DRIVER', 'INSTITUTION_STAFF', 'ADMIN', 'SAFETY_ADMIN', 'OPERATOR'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(16), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Enum('ACTIVE', 'SUSPENDED'), default='ACTIVE')
    institution_id = db.Column(db.BigInteger, db.ForeignKey('institutions.id'), nullable=True)
    failed_logins = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    students = db.relationship('Student', back_populates='guardian', foreign_keys='Student.guardian_id')
    driver = db.relationship('Driver', back_populates='user', uselist=False, foreign_keys='Driver.user_id')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_role(self, *roles):
        return self.role in roles
    
    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'role': self.role,
            'name': self.name,
            'email': self.email if include_sensitive else None,
            'phone': self.phone if include_sensitive else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        return data
