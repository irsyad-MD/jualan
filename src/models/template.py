from src.models.user import db
from datetime import datetime
import uuid

class Template(db.Model):
    __tablename__ = 'templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(255))  # Path to preview image
    price = db.Column(db.Numeric(10, 2), nullable=False)
    file_path = db.Column(db.String(255))  # Path to template file
    category = db.Column(db.String(100))  # e.g., 'landing-page', 'portfolio', 'ecommerce'
    tags = db.Column(db.Text)  # JSON string of tags
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    licenses = db.relationship('License', backref='template', lazy=True, cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='template', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Template {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'image': self.image,
            'price': float(self.price) if self.price else 0,
            'category': self.category,
            'tags': self.tags,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def generate_slug(self):
        """Generate slug from name"""
        import re
        slug = re.sub(r'[^\w\s-]', '', self.name.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')

