from backend.app.extensions import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    channel = db.Column(db.Enum('EMAIL', 'IN_APP'), nullable=False)
    template = db.Column(db.String(40), nullable=False)
    subject = db.Column(db.String(200))
    payload_json = db.Column(db.JSON)
    status = db.Column(db.Enum('QUEUED', 'SENT', 'FAILED', 'READ'), default='QUEUED')
    attempts = db.Column(db.SmallInteger, default=0)
    last_error = db.Column(db.String(255))
    related_type = db.Column(db.String(30))
    related_id = db.Column(db.BigInteger)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'channel': self.channel,
            'template': self.template,
            'subject': self.subject,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'sent_at': self.sent_at.isoformat() if self.sent_at else None
        }
