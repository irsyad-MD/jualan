from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from src.models import db, User, Template, Transaction, License
from src.middleware import admin_required
from sqlalchemy import desc, func
import os
import uuid
from datetime import datetime, timedelta

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/")
@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    """Admin dashboard"""
    # Get statistics
    stats = {
        "total_users": User.query.filter_by(role="user").count(),
        "total_templates": Template.query.count(),
        "total_transactions": Transaction.query.count(),
        "pending_transactions": Transaction.query.filter_by(status="pending").count(),
        "confirmed_transactions": Transaction.query.filter_by(status="confirmed").count(),
        "total_licenses": License.query.count(),
        "active_licenses": License.query.filter_by(status="valid").count(),
        "total_revenue": db.session.query(func.sum(Transaction.amount))\
                                  .filter_by(status="confirmed").scalar() or 0
    }
    
    # Recent transactions
    recent_transactions = Transaction.query.order_by(desc(Transaction.created_at)).limit(10).all()
    
    # Recent users
    recent_users = User.query.filter_by(role="user")\
                            .order_by(desc(User.created_at)).limit(5).all()
    
    return render_template("admin/dashboard.html", 
                         stats=stats, 
                         recent_transactions=recent_transactions,
                         recent_users=recent_users)

@admin_bp.route("/users")
@login_required
@admin_required
def users():
    """Manage users"""
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "")
    
    query = User.query.filter_by(role="user")
    
    if search:
        query = query.filter(
            db.or_(
                User.username.contains(search),
                User.email.contains(search)
            )
        )
    
    users = query.order_by(desc(User.created_at))\
                 .paginate(page=page, per_page=20, error_out=False)
    
    return render_template("admin/users.html", users=users, search=search)

@admin_bp.route("/user/delete/<int:id>", methods=["POST"])
@login_required
@admin_required
def delete_user(id):
    """Delete user"""
    user = User.query.get_or_404(id)
    if user.role == "admin":
        flash("Tidak bisa menghapus akun admin.", "error")
        return redirect(url_for("admin.users"))
    
    db.session.delete(user)
    db.session.commit()
    flash(f"User {user.username} berhasil dihapus.", "success")
    return redirect(url_for("admin.users"))

@admin_bp.route("/templates")
@login_required
@admin_required
def templates():
    """Manage templates"""
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "")
    
    query = Template.query
    
    if search:
        query = query.filter(
            db.or_(
                Template.name.contains(search),
                Template.description.contains(search)
            )
        )
    
    templates = query.order_by(desc(Template.created_at))\
                    .paginate(page=page, per_page=20, error_out=False)
    
    return render_template("admin/templates.html", templates=templates, search=search)

@admin_bp.route("/template/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_template():
    """Add new template"""
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        price = request.form.get("price", type=float)
        category = request.form.get("category")
        tags = request.form.get("tags", "")
        
        if not name or not price:
            flash("Nama dan harga template harus diisi.", "error")
            return render_template("admin/add_template.html")
        
        # Create template
        template = Template(
            name=name,
            description=description,
            price=price,
            category=category,
            tags=tags,
            is_active=True
        )
        template.slug = template.generate_slug()
        
        # Handle file upload
        if "template_file" in request.files:
            file = request.files["template_file"]
            if file and file.filename != "":
                try:
                    filename = secure_filename(f"template_{uuid.uuid4().hex[:8]}_{file.filename}")
                    upload_path = os.path.join(current_app.config.get("UPLOAD_FOLDER", "uploads"), "templates")
                    os.makedirs(upload_path, exist_ok=True)
                    file_path = os.path.join(upload_path, filename)
                    file.save(file_path)
                    template.file_path = f"uploads/templates/{filename}" # Store relative path
                except Exception as e:
                    current_app.logger.error(f"File upload error: {str(e)}")
                    flash("Gagal mengupload file template.", "error")
                    return render_template("admin/add_template.html")
        
        # Handle image upload
        if "template_image" in request.files:
            file = request.files["template_image"]
            if file and file.filename != "":
                try:
                    filename = secure_filename(f"image_{uuid.uuid4().hex[:8]}_{file.filename}")
                    upload_path = os.path.join(current_app.config.get("UPLOAD_FOLDER", "uploads"), "images")
                    os.makedirs(upload_path, exist_ok=True)
                    file_path = os.path.join(upload_path, filename)
                    file.save(file_path)
                    template.image = f"uploads/images/{filename}"
                except Exception as e:
                    current_app.logger.error(f"Image upload error: {str(e)}")
                    flash("Gagal mengupload gambar template.", "error")
                    return render_template("admin/add_template.html")
        
        try:
            db.session.add(template)
            db.session.commit()
            flash("Template berhasil ditambahkan.", "success")
            return redirect(url_for("admin.templates"))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Database error: {str(e)}")
            flash("Gagal menyimpan template ke database.", "error")
    
    return render_template("admin/add_template.html")

@admin_bp.route("/template/edit/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_template(id):
    """Edit template"""
    template = Template.query.get_or_404(id)
    
    if request.method == "POST":
        template.name = request.form.get("name")
        template.description = request.form.get("description")
        template.price = request.form.get("price", type=float)
        template.category = request.form.get("category")
        template.tags = request.form.get("tags", "")
        template.is_active = bool(request.form.get("is_active"))
        
        # Handle file upload
        if "template_file" in request.files:
            file = request.files["template_file"]
            if file and file.filename != "":
                try:
                    filename = secure_filename(f"template_{uuid.uuid4().hex[:8]}_{file.filename}")
                    upload_path = os.path.join(current_app.config.get("UPLOAD_FOLDER", "uploads"), "templates")
                    os.makedirs(upload_path, exist_ok=True)
                    file_path = os.path.join(upload_path, filename)
                    file.save(file_path)
                    template.file_path = f"uploads/templates/{filename}" # Store relative path
                except Exception as e:
                    current_app.logger.error(f"File upload error: {str(e)}")
                    flash("Gagal mengupload file template.", "error")
                    return render_template("admin/edit_template.html", template=template)
        
        # Handle image upload
        if "template_image" in request.files:
            file = request.files["template_image"]
            if file and file.filename != "":
                try:
                    filename = secure_filename(f"image_{uuid.uuid4().hex[:8]}_{file.filename}")
                    upload_path = os.path.join(current_app.config.get("UPLOAD_FOLDER", "uploads"), "images")
                    os.makedirs(upload_path, exist_ok=True)
                    file_path = os.path.join(upload_path, filename)
                    file.save(file_path)
                    template.image = f"uploads/images/{filename}"
                except Exception as e:
                    current_app.logger.error(f"Image upload error: {str(e)}")
                    flash("Gagal mengupload gambar template.", "error")
                    return render_template("admin/edit_template.html", template=template)
        
        try:
            db.session.commit()
            flash("Template berhasil diupdate.", "success")
            return redirect(url_for("admin.templates"))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Database error: {str(e)}")
            flash("Gagal menyimpan perubahan template.", "error")
    
    return render_template("admin/edit_template.html", template=template)

@admin_bp.route("/template/delete/<int:id>", methods=["POST"])
@login_required
@admin_required
def delete_template(id):
    """Delete template"""
    template = Template.query.get_or_404(id)
    
    # Delete associated files if they exist
    if template.file_path and os.path.exists(os.path.join(current_app.root_path, "static", template.file_path)):
        os.remove(os.path.join(current_app.root_path, "static", template.file_path))
    if template.image and os.path.exists(os.path.join(current_app.root_path, "static", template.image)):
        os.remove(os.path.join(current_app.root_path, "static", template.image))
        
    db.session.delete(template)
    db.session.commit()
    flash("Template berhasil dihapus.", "success")
    return redirect(url_for("admin.templates"))

@admin_bp.route("/transactions")
@login_required
@admin_required
def transactions():
    """Manage transactions"""
    page = request.args.get("page", 1, type=int)
    status = request.args.get("status", "")
    
    query = Transaction.query
    
    if status:
        query = query.filter_by(status=status)
    
    transactions = query.order_by(desc(Transaction.created_at))\
                       .paginate(page=page, per_page=20, error_out=False)
    
    return render_template("admin/transactions.html", transactions=transactions, current_status=status)

@admin_bp.route("/transaction/<int:id>")
@login_required
@admin_required
def transaction_detail(id):
    """Transaction detail"""
    transaction = Transaction.query.get_or_404(id)
    return render_template("admin/transaction_detail.html", transaction=transaction)

@admin_bp.route("/transaction/<int:id>/confirm", methods=["POST"])
@login_required
@admin_required
def confirm_transaction(id):
    """Confirm transaction and create license"""
    transaction = Transaction.query.get_or_404(id)
    
    if transaction.status != "pending":
        flash("Transaksi sudah diproses.", "error")
        return redirect(url_for("admin.transaction_detail", id=id))
    
    admin_note = request.form.get("admin_note", "")
    
    # Confirm transaction
    transaction.confirm(admin_note)
    
    # Create license
    license = License(
        user_id=transaction.user_id,
        template_id=transaction.template_id,
        license_key=str(uuid.uuid4()),
        status="valid"
    )
    
    db.session.add(license)
    db.session.commit()
    
    flash("Transaksi berhasil dikonfirmasi dan lisensi telah dibuat.", "success")
    
    # Here you could implement WhatsApp notification
    # For now, just show the WhatsApp number in flash message
    flash(f"Hubungi pembeli di WhatsApp: {transaction.whatsapp_number}", "info")
    
    return redirect(url_for("admin.transaction_detail", id=id))

@admin_bp.route("/transaction/<int:id>/reject", methods=["POST"])
@login_required
@admin_required
def reject_transaction(id):
    """Reject transaction"""
    transaction = Transaction.query.get_or_404(id)
    
    if transaction.status != "pending":
        flash("Transaksi sudah diproses.", "error")
        return redirect(url_for("admin.transaction_detail", id=id))
    
    admin_note = request.form.get("admin_note", "")
    transaction.reject(admin_note)
    
    flash("Transaksi berhasil ditolak.", "success")
    return redirect(url_for("admin.transaction_detail", id=id))

@admin_bp.route("/licenses")
@login_required
@admin_required
def licenses():
    """Manage licenses"""
    page = request.args.get("page", 1, type=int)
    status = request.args.get("status", "")
    
    query = License.query
    
    if status:
        query = query.filter_by(status=status)
    
    licenses = query.order_by(desc(License.created_at))\
                   .paginate(page=page, per_page=20, error_out=False)
    
    return render_template("admin/licenses.html", licenses=licenses, current_status=status)

@admin_bp.route("/license/<int:id>/revoke", methods=["POST"])
@login_required
@admin_required
def revoke_license(id):
    """Revoke license"""
    license = License.query.get_or_404(id)
    license.revoke()
    
    flash("Lisensi berhasil dicabut.", "success")
    return redirect(url_for("admin.licenses"))



