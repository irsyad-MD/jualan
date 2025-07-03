from src.models.user import db
from datetime import datetime

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('templates.id'), nullable=False)
    status = db.Column(db.Enum('pending', 'confirmed', 'rejected', 'expired', name='transaction_status'), 
                      default='pending', nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(50))  # e.g., 'transfer', 'ewallet'
    payment_proof = db.Column(db.String(255))  # Path to payment proof image
    note = db.Column(db.Text)
    admin_note = db.Column(db.Text)  # Admin's note about the transaction
    whatsapp_number = db.Column(db.String(20))  # User's WhatsApp number for contact
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Transaction {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'template_id': self.template_id,
            'status': self.status,
            'amount': float(self.amount) if self.amount else 0,
            'payment_method': self.payment_method,
            'payment_proof': self.payment_proof,
            'note': self.note,
            'admin_note': self.admin_note,
            'whatsapp_number': self.whatsapp_number,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'confirmed_at': self.confirmed_at.isoformat() if self.confirmed_at else None
        }
    
    def confirm(self, admin_note=None):
        """Confirm transaction"""
        self.status = 'confirmed'
        self.confirmed_at = datetime.utcnow()
        if admin_note:
            self.admin_note = admin_note
        db.session.commit()
    
    def reject(self, admin_note=None):
        """Reject transaction"""
        self.status = 'rejected'
        if admin_note:
            self.admin_note = admin_note
        db.session.commit()
    
    def expire(self):
        """Expire transaction"""
        self.status = 'expired'
        db.session.commit()

