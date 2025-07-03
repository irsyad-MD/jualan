from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from src.models import db, Template, Transaction, License
from sqlalchemy import desc

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Landing page"""
    # Get featured templates
    featured_templates = Template.query.filter_by(is_active=True).limit(6).all()
    return render_template('main/index.html', featured_templates=featured_templates)

@main_bp.route('/about')
def about():
    """About page"""
    return render_template('main/about.html')

@main_bp.route('/services')
def services():
    """Services page"""
    return render_template('main/services.html')

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Here you could implement email sending or save to database
        # For now, just show success message
        flash('Pesan Anda telah dikirim. Kami akan segera menghubungi Anda.', 'success')
        return redirect(url_for('main.contact'))
    
    return render_template('main/contact.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    if current_user.is_admin():
        return redirect(url_for('admin.dashboard'))
    
    # Get user's transactions
    transactions = Transaction.query.filter_by(user_id=current_user.id)\
                                  .order_by(desc(Transaction.created_at))\
                                  .limit(10).all()
    
    # Get user's licenses
    licenses = License.query.filter_by(user_id=current_user.id)\
                           .order_by(desc(License.created_at))\
                           .limit(10).all()
    
    # Get statistics
    stats = {
        'total_purchases': Transaction.query.filter_by(user_id=current_user.id).count(),
        'confirmed_purchases': Transaction.query.filter_by(user_id=current_user.id, status='confirmed').count(),
        'active_licenses': License.query.filter_by(user_id=current_user.id, status='valid').count(),
        'pending_transactions': Transaction.query.filter_by(user_id=current_user.id, status='pending').count()
    }
    
    return render_template('main/dashboard.html', 
                         transactions=transactions, 
                         licenses=licenses, 
                         stats=stats)

@main_bp.route('/templates')
def templates():
    """Template catalog page"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    sort_by = request.args.get('sort', 'newest')
    
    query = Template.query.filter_by(is_active=True)
    
    # Filter by category
    if category:
        query = query.filter_by(category=category)
    
    # Search by name or description
    if search:
        query = query.filter(
            db.or_(
                Template.name.contains(search),
                Template.description.contains(search)
            )
        )
    
    # Sort
    if sort_by == 'newest':
        query = query.order_by(desc(Template.created_at))
    elif sort_by == 'oldest':
        query = query.order_by(Template.created_at)
    elif sort_by == 'price_low':
        query = query.order_by(Template.price)
    elif sort_by == 'price_high':
        query = query.order_by(desc(Template.price))
    elif sort_by == 'name':
        query = query.order_by(Template.name)
    
    # Pagination
    per_page = 12
    templates = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get categories for filter
    categories = db.session.query(Template.category)\
                          .filter(Template.is_active == True)\
                          .distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    return render_template('main/templates.html', 
                         templates=templates, 
                         categories=categories,
                         current_category=category,
                         current_search=search,
                         current_sort=sort_by)

@main_bp.route('/template/<int:id>')
def template_detail(id):
    """Template detail page"""
    template = Template.query.get_or_404(id)
    
    if not template.is_active:
        flash('Template tidak tersedia.', 'error')
        return redirect(url_for('main.templates'))
    
    # Check if user already has license for this template
    user_license = None
    if current_user.is_authenticated:
        user_license = License.query.filter_by(
            user_id=current_user.id,
            template_id=template.id
        ).first()
    
    # Get related templates
    related_templates = Template.query.filter(
        Template.category == template.category,
        Template.id != template.id,
        Template.is_active == True
    ).limit(4).all()
    
    return render_template('main/template_detail.html', 
                         template=template, 
                         user_license=user_license,
                         related_templates=related_templates)

