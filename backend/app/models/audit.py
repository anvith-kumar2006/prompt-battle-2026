from backend.app.extensions import db
from datetime import datetime

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    actor_user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(60), nullable=False)
    entity_type = db.Column(db.String(30))
    entity_id = db.Column(db.BigInteger)
    detail_json = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @staticmethod
    def log(actor_id, action, entity_type=None, entity_id=None, details=None, ip=None):
        """Convenience method to create audit logs"""
        log = AuditLog(
            actor_user_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            detail_json=details,
            ip_address=ip
        )
        db.session.add(log)
        return log
