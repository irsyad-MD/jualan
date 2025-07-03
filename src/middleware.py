from functools import wraps
from flask import abort, request, jsonify, flash, redirect, url_for
from flask_login import current_user
from src.models import License, Template

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin():
            flash('Akses ditolak. Hanya admin yang dapat mengakses halaman ini.', 'error')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function

def license_required(template_id_param='id'):
    """Decorator to require valid license for template access"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            
            # Get template_id from URL parameters or kwargs
            template_id = kwargs.get(template_id_param) or kwargs.get('id') or request.args.get(template_id_param) or request.args.get('id')
            
            if not template_id:
                flash('Template ID tidak ditemukan.', 'error')
                return redirect(url_for('main.dashboard'))
            
            # Check if template exists
            template = Template.query.get(template_id)
            if not template:
                flash('Template tidak ditemukan.', 'error')
                return redirect(url_for('main.dashboard'))
            
            # Check if user has valid license for this template
            license = License.query.filter_by(
                user_id=current_user.id,
                template_id=template_id,
                status='valid'
            ).first()
            
            if not license or not license.is_valid():
                flash('Anda tidak memiliki lisensi yang valid untuk template ini.', 'error')
                return redirect(url_for('main.template_detail', id=template_id))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def api_license_required(f):
    """Decorator for API endpoints to require valid license"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        license_key = request.headers.get('X-License-Key') or request.args.get('license_key')
        
        if not license_key:
            return jsonify({'error': 'License key required'}), 401
        
        license = License.query.filter_by(license_key=license_key).first()
        
        if not license or not license.is_valid():
            return jsonify({'error': 'Invalid or expired license'}), 403
        
        # Add license info to request context
        request.license = license
        
        return f(*args, **kwargs)
    return decorated_function

def validate_template_access(template_id, user_id):
    """Helper function to validate template access"""
    template = Template.query.get(template_id)
    if not template:
        return False, 'Template tidak ditemukan.'
    
    if not template.is_active:
        return False, 'Template tidak aktif.'
    
    license = License.query.filter_by(
        user_id=user_id,
        template_id=template_id,
        status='valid'
    ).first()
    
    if not license or not license.is_valid():
        return False, 'Lisensi tidak valid atau sudah expired.'
    
    return True, None

def cors_headers(f):
    """Add CORS headers to response"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        
        if hasattr(response, 'headers'):
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-License-Key'
        
        return response
    return decorated_function

