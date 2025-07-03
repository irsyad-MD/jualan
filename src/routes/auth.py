from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from src.models import db, User
import re
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message

from flask import current_app
from datetime import datetime, timedelta

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        remember = bool(request.form.get("remember"))
        
        if not username or not password:
            flash("Username dan password harus diisi.", "error")
            return render_template("auth/login.html")
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user, remember=remember)
            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)
            return redirect(url_for("main.dashboard"))
        else:
            flash("Username atau password salah.", "error")
    
    return render_template("auth/login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        # Validation
        errors = []
        
        if not username or len(username) < 3:
            errors.append("Username minimal 3 karakter.")
        
        if not email or not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
            errors.append("Email tidak valid.")
        
        if not password or len(password) < 6:
            errors.append("Password minimal 6 karakter.")
        
        if password != confirm_password:
            errors.append("Konfirmasi password tidak cocok.")
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            errors.append("Username sudah digunakan.")
        
        if User.query.filter_by(email=email).first():
            errors.append("Email sudah digunakan.")
        
        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("auth/register.html")
        
        # Create new user
        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            role="user"
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash("Registrasi berhasil! Silakan login.", "success")
        return redirect(url_for("auth.login"))
    
    return render_template("auth/register.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Anda telah logout.", "info")
    return redirect(url_for("main.index"))

@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        email = request.form.get("email")
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")
        
        errors = []
        
        # Validate email
        if not email or not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
            errors.append("Email tidak valid.")
        
        # Check if email is already used by another user
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != current_user.id:
            errors.append("Email sudah digunakan.")
        
        # If changing password
        if new_password:
            if not current_password:
                errors.append("Password saat ini harus diisi.")
            elif not check_password_hash(current_user.password, current_password):
                errors.append("Password saat ini salah.")
            elif len(new_password) < 6:
                errors.append("Password baru minimal 6 karakter.")
            elif new_password != confirm_password:
                errors.append("Konfirmasi password tidak cocok.")
        
        if errors:
            for error in errors:
                flash(error, "error")
        else:
            # Update user
            current_user.email = email
            if new_password:
                current_user.password = generate_password_hash(new_password)
            
            db.session.commit()
            flash("Profile berhasil diupdate.", "success")
    
    return render_template("auth/profile.html")


@auth_bp.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    """Forgot password page"""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    
    if request.method == "POST":
        email = request.form.get("email")
        
        if not email:
            flash("Email harus diisi.", "error")
            return render_template("auth/forgot_password.html")
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            send_reset_email(user)
            flash("Link reset password telah dikirim ke email Anda. Silakan cek email Anda.", "success")
        else:
            # Don't reveal if email exists or not for security
            flash("Link reset password telah dikirim ke email Anda. Silakan cek email Anda.", "success")
    
    return render_template("auth/forgot_password.html")

@auth_bp.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """Reset password with token"""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    
    token_serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        email = token_serializer.loads(token, salt="password-reset-salt", max_age=3600) # Token valid for 1 hour
    except:
        flash("Link reset password tidak valid atau telah kadaluarsa.", "error")
        return redirect(url_for("auth.forgot_password"))

    user = User.query.filter_by(email=email).first()
    if not user or user.reset_token != token or user.reset_token_expiration < datetime.utcnow():
        flash("Link reset password tidak valid atau telah kadaluarsa.", "error")
        return redirect(url_for("auth.forgot_password"))
    
    if request.method == "POST":
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        errors = []
        
        if not password or len(password) < 6:
            errors.append("Password minimal 6 karakter.")
        
        if password != confirm_password:
            errors.append("Konfirmasi password tidak cocok.")
        
        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("auth/reset_password.html", token=token)
        
        user.password = generate_password_hash(password)
        user.reset_token = None
        user.reset_token_expiration = None
        db.session.commit()
        
        flash("Password berhasil direset. Silakan login dengan password baru.", "success")
        return redirect(url_for("auth.login"))
    
    return render_template("auth/reset_password.html", token=token)

def send_reset_email(user):
    from src.main import mail
    import os  # Pastikan os digunakan untuk ambil env

    token_serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    token = token_serializer.dumps(user.email, salt="password-reset-salt")
    
    reset_link = url_for("auth.reset_password", token=token, _external=True)
    
    msg = Message(
        subject="Permintaan Reset Password Anda",
        sender=os.getenv("imsyad8@gmail.com"),  # ✅ Ganti ini agar 100% sesuai akun Gmail
        recipients=[user.email]
    )
    
    msg.body = (
        f"Untuk mereset password Anda, kunjungi link berikut:\n{reset_link}\n\n"
        "Link ini akan kadaluarsa dalam 1 jam."
    )
    
    mail.send(msg)
    
    user.reset_token = token
    user.reset_token_expiration = datetime.utcnow() + timedelta(hours=1)
    db.session.commit()



