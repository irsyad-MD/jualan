from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from src.models import db, Template, Transaction, License
from src.middleware import license_required, api_license_required
import os
import uuid
from datetime import datetime

template_bp = Blueprint("template", __name__)

@template_bp.route("/buy/<int:id>", methods=["GET", "POST"])
@login_required
def buy(id):
    """Template purchase page"""
    template = Template.query.get_or_404(id)
    
    if not template.is_active:
        flash("Template tidak tersedia untuk dibeli.", "error")
        return redirect(url_for("main.template_detail", id=id))
    
    # Check if user already has this template
    existing_license = License.query.filter_by(
        user_id=current_user.id,
        template_id=template.id
    ).first()
    
    if existing_license and existing_license.status == "valid":
        flash("Anda sudah memiliki lisensi untuk template ini.", "info")
        return redirect(url_for("main.template_detail", id=id))
    
    # Check if user has pending transaction for this template
    pending_transaction = Transaction.query.filter_by(
        user_id=current_user.id,
        template_id=template.id,
        status="pending"
    ).first()
    
    if pending_transaction:
        flash("Anda sudah memiliki transaksi pending untuk template ini.", "info")
        return redirect(url_for("template.checkout", transaction_id=pending_transaction.id))
    
    if request.method == "POST":
        whatsapp_number = request.form.get("whatsapp_number")
        payment_method = request.form.get("payment_method")
        note = request.form.get("note", "")
        
        if not whatsapp_number:
            flash("Nomor WhatsApp harus diisi.", "error")
            return render_template("template/buy.html", template=template)
        
        if not payment_method:
            flash("Metode pembayaran harus dipilih.", "error")
            return render_template("template/buy.html", template=template)
        
        # Create transaction
        transaction = Transaction(
            user_id=current_user.id,
            template_id=template.id,
            amount=template.price,
            payment_method=payment_method,
            whatsapp_number=whatsapp_number,
            note=note,
            status="pending"
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        flash("Transaksi berhasil dibuat. Silakan lanjutkan ke pembayaran.", "success")
        return redirect(url_for("template.checkout", transaction_id=transaction.id))
    
    return render_template("template/buy.html", template=template)

@template_bp.route("/checkout/<int:transaction_id>", methods=["GET", "POST"])
@login_required
def checkout(transaction_id):
    """Checkout page"""
    transaction = Transaction.query.get_or_404(transaction_id)
    
    # Check if transaction belongs to current user
    if transaction.user_id != current_user.id:
        flash("Transaksi tidak ditemukan.", "error")
        return redirect(url_for("main.dashboard"))
    
    if transaction.status != "pending":
        flash("Transaksi sudah diproses.", "info")
        return redirect(url_for("main.dashboard"))
    
    if request.method == "POST":
        # Handle payment proof upload
        if "payment_proof" not in request.files:
            flash("Bukti pembayaran harus diupload.", "error")
            return render_template("template/checkout.html", transaction=transaction)
        
        file = request.files["payment_proof"]
        if file.filename == "":
            flash("Bukti pembayaran harus diupload.", "error")
            return render_template("template/checkout.html", transaction=transaction)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(f"payment_{transaction.id}_{uuid.uuid4().hex[:8]}_{file.filename}")
            upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], "payments")
            os.makedirs(upload_path, exist_ok=True)
            file_path = os.path.join(upload_path, filename)
            file.save(file_path)
            
            # Update transaction
            transaction.payment_proof = f"uploads/payments/{filename}"
            transaction.updated_at = datetime.utcnow()
            db.session.commit()
            
            flash("Bukti pembayaran berhasil diupload. Transaksi akan diproses dalam 1x24 jam.", "success")
            return redirect(url_for("main.dashboard"))
        else:
            flash("Format file tidak didukung. Gunakan JPG, PNG, atau PDF.", "error")
    
    return render_template("template/checkout.html", transaction=transaction)

@template_bp.route("/download/<int:id>")
@login_required
@license_required()
def download(id):
    """Download template file"""
    try:
        current_app.logger.info(f"Download request for template ID: {id} by user: {current_user.id}")
        
        template = Template.query.get_or_404(id)
        current_app.logger.info(f"Template found: {template.name}, file_path: {template.file_path}")
        
        if not template.file_path:
            current_app.logger.error(f"Template {id} has no file_path")
            flash("File template tidak ditemukan.", "error")
            return redirect(url_for("main.template_detail", id=id))
        
        # Try multiple possible paths for the file
        possible_paths = [
            os.path.join(current_app.root_path, "static", template.file_path),
            os.path.join(current_app.root_path, template.file_path),
            os.path.join(current_app.config.get("UPLOAD_FOLDER", "uploads"), template.file_path.replace("uploads/", "")),
            os.path.join(current_app.root_path, "src", "static", "uploads", "templates", os.path.basename(template.file_path)),
            template.file_path  # In case it's already an absolute path
        ]
        
        current_app.logger.info(f"Checking paths: {possible_paths}")
        
        full_file_path = None
        for path in possible_paths:
            current_app.logger.info(f"Checking path: {path}")
            if os.path.exists(path):
                full_file_path = path
                current_app.logger.info(f"File found at: {path}")
                break
            else:
                current_app.logger.info(f"File not found at: {path}")
        
        if not full_file_path:
            current_app.logger.error(f"File not found in any of the paths for template {id}")
            flash("File template tidak ditemukan di server.", "error")
            return redirect(url_for("main.template_detail", id=id))
        
        # Get the original filename or use template slug
        download_name = f"{template.slug}.zip"
        if template.file_path:
            original_filename = os.path.basename(template.file_path)
            if original_filename and original_filename != template.file_path:
                download_name = original_filename
        
        current_app.logger.info(f"Sending file: {full_file_path} as {download_name}")
        return send_file(full_file_path, as_attachment=True, 
                        download_name=download_name)
                        
    except Exception as e:
        current_app.logger.error(f"Download error for template {id}: {str(e)}")
        flash("Terjadi kesalahan saat mengunduh file. Silakan coba lagi.", "error")
        return redirect(url_for("main.template_detail", id=id))

@template_bp.route("/preview/<int:id>")
@login_required
@license_required()
def preview(id):
    """Preview template"""
    template = Template.query.get_or_404(id)
    
    # Here you could implement template preview functionality
    # For now, just show template details
    return render_template("template/preview.html", template=template)

@template_bp.route("/api/validate-license")
@api_license_required
def validate_license():
    """API endpoint to validate license"""
    license = request.license
    template = Template.query.get(license.template_id)
    
    return jsonify({
        "valid": True,
        "license_key": license.license_key,
        "template": {
            "id": template.id,
            "name": template.name,
            "slug": template.slug
        },
        "user": {
            "id": license.user.id,
            "username": license.user.username
        },
        "expires_at": license.expires_at.isoformat() if license.expires_at else None
    })

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf"}
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS



