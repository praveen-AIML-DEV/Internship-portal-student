from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash
from models import User, Student, Company, College
from config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

auth_bp = Blueprint('auth', __name__)
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(bind=engine)

def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(id=user_id).first()
        return user
    finally:
        db.close()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'user_id' in session:
            role = session.get('role')
            if role == 'student': return redirect(url_for('student.dashboard'))
            if role == 'company': return redirect(url_for('company.dashboard'))
            if role == 'college': return redirect(url_for('college.dashboard'))
            if role == 'admin': return redirect(url_for('admin.dashboard'))
        return render_template('login.html')

    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()

    db = SessionLocal()
    try:
        user = db.query(User).filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash('Invalid email or password', 'danger')
            return render_template('login.html', email=email), 401

        session['user_id'] = user.id
        session['email'] = user.email
        session['role'] = user.role

        if user.role == 'student' and user.student_profile:
            session['profile_id'] = user.student_profile.id
            session['name'] = user.student_profile.full_name
            return redirect(url_for('student.dashboard'))
        elif user.role == 'company' and user.company_profile:
            session['profile_id'] = user.company_profile.id
            session['name'] = user.company_profile.company_name
            return redirect(url_for('company.dashboard'))
        elif user.role == 'college' and user.college_profile:
            session['profile_id'] = user.college_profile.id
            session['name'] = user.college_profile.college_name
            return redirect(url_for('college.dashboard'))
        elif user.role == 'admin':
            session['name'] = 'System Administrator'
            return redirect(url_for('admin.dashboard'))

        flash('User profile not fully initialized', 'warning')
        return redirect(url_for('auth.login'))
    finally:
        db.close()


@auth_bp.route('/register', methods=['POST'])
def register():
    role = request.form.get('role', 'student').strip().lower()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()
    name = request.form.get('name', '').strip()

    if not email or not password or not name:
        flash('All fields are required', 'danger')
        return redirect(url_for('auth.login'))

    db = SessionLocal()
    try:
        existing = db.query(User).filter_by(email=email).first()
        if existing:
            flash('Account with this email already exists', 'danger')
            return redirect(url_for('auth.login'))

        user = User(email=email, role=role)
        user.set_password(password)
        db.add(user)
        db.flush()

        if role == 'student':
            slug = name.lower().replace(' ', '-') + f"-{user.id}"
            stu = Student(
                user_id=user.id,
                full_name=name,
                portfolio_slug=slug,
                degree=request.form.get('degree', 'B.Tech'),
                branch=request.form.get('branch', 'Computer Science')
            )
            db.add(stu)
            db.commit()
            session['user_id'] = user.id
            session['email'] = user.email
            session['role'] = role
            session['profile_id'] = stu.id
            session['name'] = stu.full_name
            flash('Registration successful! Welcome to the portal.', 'success')
            return redirect(url_for('student.dashboard'))

        elif role == 'company':
            comp = Company(
                user_id=user.id,
                company_name=name,
                industry_type=request.form.get('industry_type', 'Technology'),
                location=request.form.get('location', 'Bengaluru, India')
            )
            db.add(comp)
            db.commit()
            session['user_id'] = user.id
            session['email'] = user.email
            session['role'] = role
            session['profile_id'] = comp.id
            session['name'] = comp.company_name
            flash('Company registered successfully!', 'success')
            return redirect(url_for('company.dashboard'))

        elif role == 'college':
            col = College(
                user_id=user.id,
                college_name=name,
                code=request.form.get('code', 'INST-01'),
                location=request.form.get('location', 'India')
            )
            db.add(col)
            db.commit()
            session['user_id'] = user.id
            session['email'] = user.email
            session['role'] = role
            session['profile_id'] = col.id
            session['name'] = col.college_name
            flash('College registered successfully!', 'success')
            return redirect(url_for('college.dashboard'))

        db.commit()
        return redirect(url_for('auth.login'))
    except Exception as e:
        db.rollback()
        flash(f'Registration error: {str(e)}', 'danger')
        return redirect(url_for('auth.login'))
    finally:
        db.close()


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@auth_bp.route('/switch-role/<target_role>')
def switch_role(target_role):
    """
    Demo Helper: Instantly switch active session to pre-seeded role
    so judges/reviewers can test without re-logging in!
    """
    db = SessionLocal()
    try:
        target_role = target_role.lower()
        if target_role == 'student':
            user = db.query(User).filter_by(email='student@demo.edu').first()
            if user and user.student_profile:
                session['user_id'] = user.id
                session['email'] = user.email
                session['role'] = 'student'
                session['profile_id'] = user.student_profile.id
                session['name'] = user.student_profile.full_name
                flash(f'Switched to Student Demo Account: {user.student_profile.full_name}', 'info')
                return redirect(url_for('student.dashboard'))

        elif target_role == 'company':
            user = db.query(User).filter_by(email='hr@techcorp.com').first()
            if user and user.company_profile:
                session['user_id'] = user.id
                session['email'] = user.email
                session['role'] = 'company'
                session['profile_id'] = user.company_profile.id
                session['name'] = user.company_profile.company_name
                flash(f'Switched to Company Demo Account: {user.company_profile.company_name}', 'info')
                return redirect(url_for('company.dashboard'))

        elif target_role == 'college':
            user = db.query(User).filter_by(email='dean@university.edu').first()
            if user and user.college_profile:
                session['user_id'] = user.id
                session['email'] = user.email
                session['role'] = 'college'
                session['profile_id'] = user.college_profile.id
                session['name'] = user.college_profile.college_name
                flash(f'Switched to College Demo Account: {user.college_profile.college_name}', 'info')
                return redirect(url_for('college.dashboard'))

        elif target_role == 'admin':
            user = db.query(User).filter_by(email='admin@portal.gov').first()
            if user:
                session['user_id'] = user.id
                session['email'] = user.email
                session['role'] = 'admin'
                session['name'] = 'System Administrator'
                flash('Switched to Admin Demo Account', 'info')
                return redirect(url_for('admin.dashboard'))

        flash('Target demo account not found', 'warning')
        return redirect(url_for('auth.login'))
    finally:
        db.close()


# JSON REST APIs
@auth_bp.route('/api/auth/me')
def api_me():
    user = get_current_user()
    if not user:
        return jsonify({'authenticated': False}), 200
    return jsonify({
        'authenticated': True,
        'user_id': user.id,
        'email': user.email,
        'role': user.role,
        'name': session.get('name'),
        'profile_id': session.get('profile_id')
    }), 200
