from functools import wraps
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Config
from models import User, Student, Company, College, Job, Internship, Certificate, Skill, Application

admin_bp = Blueprint('admin', __name__)
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(bind=engine)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Admin authentication required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/admin/dashboard')
@admin_required
def dashboard():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        students = db.query(Student).all()
        companies = db.query(Company).all()
        colleges = db.query(College).all()
        jobs = db.query(Job).all()
        internships = db.query(Internship).all()
        certificates = db.query(Certificate).all()
        skills = db.query(Skill).all()
        applications = db.query(Application).all()

        return render_template(
            'admin/dashboard.html',
            total_users=len(users),
            students=students,
            companies=companies,
            colleges=colleges,
            jobs=jobs,
            internships=internships,
            certificates=certificates,
            skills=skills,
            applications=applications
        )
    finally:
        db.close()

@admin_bp.route('/api/admin/verify-company/<int:company_id>', methods=['POST'])
@admin_required
def verify_company(company_id):
    db = SessionLocal()
    try:
        company = db.query(Company).filter_by(id=company_id).first()
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        company.verified = not company.verified
        db.commit()
        return jsonify({'success': True, 'verified': company.verified})
    finally:
        db.close()

@admin_bp.route('/api/admin/verify-certificate/<int:cert_id>', methods=['POST'])
@admin_required
def verify_certificate(cert_id):
    db = SessionLocal()
    try:
        cert = db.query(Certificate).filter_by(id=cert_id).first()
        if not cert:
            return jsonify({'error': 'Certificate not found'}), 404
        cert.status = 'Verified' if cert.status != 'Verified' else 'Pending'
        db.commit()
        return jsonify({'success': True, 'status': cert.status})
    finally:
        db.close()
