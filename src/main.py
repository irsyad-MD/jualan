import os
import sys
from dotenv import load_dotenv
load_dotenv()
# DON\'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_login import LoginManager
from src.models import db, User, Template, License, Transaction
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.admin import admin_bp
from src.routes.template import template_bp
from src.routes.main import main_bp
from flask_mail import Mail

app = Flask(__name__, 
           static_folder=os.path.join(os.path.dirname(__file__), 'static'),
           template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

# Configuration
app.config['SECRET_KEY'] = 'imsydz-dev-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Flask-Mail configuration
app.config["MAIL_SERVER"] = "smtp.googlemail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME") or "noreply@example.com"
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = app.config["MAIL_USERNAME"]  # ✅ ini penting!

mail = Mail(app)


# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Silakan login untuk mengakses halaman ini.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(template_bp, url_prefix='/template')

# Create upload directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'templates'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'payments'), exist_ok=True)

# Initialize database
with app.app_context():
    db.create_all()
    
    # Add custom Jinja2 filters
    import json
    
    @app.template_filter('from_json')
    def from_json_filter(value):
        try:
            return json.loads(value) if value else []
        except:
            return []
    
    # Create default admin user if not exists
    admin_user = User.query.filter_by(username='imsyad').first()
    if not admin_user:
        from werkzeug.security import generate_password_hash
        admin_user = User(
            username='imsyad',
            email='imsyad8@gmail.com',
            password=generate_password_hash('imsyad1373'),
            role='admin'
        )
        db.session.add(admin_user)
        db.session.commit()
    
    # Create sample templates if not exist
    if Template.query.count() == 0:
        sample_templates = [
            {
                'name': 'Modern Landing Page',
                'slug': 'modern-landing-page',
                'description': 'Template landing page modern dengan desain responsif dan animasi menarik. Cocok untuk startup dan bisnis digital.',
                'price': 150000,
                'category': 'landing-page',
                'tags': '["modern", "responsive", "startup", "business"]'
            },
            {
                'name': 'Portfolio Creative',
                'slug': 'portfolio-creative',
                'description': 'Template portfolio kreatif untuk designer, developer, dan freelancer. Menampilkan karya dengan gaya yang elegan.',
                'price': 200000,
                'category': 'portfolio',
                'tags': '["portfolio", "creative", "designer", "freelancer"]'
            },
            {
                'name': 'E-Commerce Store',
                'slug': 'ecommerce-store',
                'description': 'Template toko online lengkap dengan fitur keranjang belanja, checkout, dan manajemen produk.',
                'price': 500000,
                'category': 'ecommerce',
                'tags': '["ecommerce", "store", "shopping", "online-shop"]'
            },
            {
                'name': 'Company Profile',
                'slug': 'company-profile',
                'description': 'Template company profile profesional untuk perusahaan dan organisasi. Dilengkapi dengan halaman tentang, layanan, dan kontak.',
                'price': 300000,
                'category': 'corporate',
                'tags': '["corporate", "company", "professional", "business"]'
            }
        ]
        
        for template_data in sample_templates:
            template = Template(**template_data)
            db.session.add(template)
        
        db.session.commit()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


