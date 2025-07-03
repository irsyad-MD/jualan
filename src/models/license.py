from src.models.user import db
from datetime import datetime
import uuid

class License(db.Model):
    __tablename__ = 'licenses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('templates.id'), nullable=False)
    license_key = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.Enum('pending', 'valid', 'expired', 'revoked', name='license_status'), 
                      default='pending', nullable=False)
    expires_at = db.Column(db.DateTime)  # Optional expiration date
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<License {self.license_key}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'template_id': self.template_id,
            'license_key': self.license_key,
            'status': self.status,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def generate_license_key(self):
        """Generate unique license key"""
        return str(uuid.uuid4())
    
    def is_valid(self):
        """Check if license is valid"""
        if self.status != 'valid':
            return False
        
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
            
        return True
    
    def activate(self):
        """Activate license"""
        self.status = 'valid'
        db.session.commit()
    
    def revoke(self):
        """Revoke license"""
        self.status = 'revoked'
        db.session.commit()

