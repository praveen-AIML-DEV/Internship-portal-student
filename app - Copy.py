import os
from flask import Flask, render_template, session, redirect, url_for
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Config
from models import Base, User, Student, Company, College, Job, Internship, Skill
from routes.auth_routes import auth_bp
from routes.student_routes import student_bp
from routes.company_routes import company_bp
from routes.college_routes import college_bp
from routes.admin_routes import admin_bp
from routes.api_routes import api_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(college_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    # Global Template Context Processor
    @app.context_processor
    def inject_global_vars():
        return {
            'user_id': session.get('user_id'),
            'user_role': session.get('role'),
            'user_name': session.get('name'),
            'profile_id': session.get('profile_id'),
            'current_year': 2026
        }

    # Landing Page Route
    @app.route('/')
    def index():
        engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        try:
            total_students = db.query(Student).count()
            total_companies = db.query(Company).count()
            total_colleges = db.query(College).count()
            total_jobs = db.query(Job).count() + db.query(Internship).count()
            total_skills = db.query(Skill).count()

            recent_jobs = db.query(Job).filter_by(status='Open').limit(3).all()
            recent_internships = db.query(Internship).filter_by(status='Open').limit(3).all()

            return render_template(
                'index.html',
                total_students=total_students,
                total_companies=total_companies,
                total_colleges=total_colleges,
                total_jobs=total_jobs,
                total_skills=total_skills,
                recent_jobs=recent_jobs,
                recent_internships=recent_internships
            )
        finally:
            db.close()

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', content='<div class=\"text-center py-20\"><h1 class=\"text-4xl font-bold text-gray-800 mb-4\">404</h1><p class=\"text-gray-600\">Page Not Found</p><a href=\"/\" class=\"mt-4 inline-block px-4 py-2 bg-indigo-600 text-white rounded-lg\">Go Home</a></div>'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('base.html', content='<div class=\"text-center py-20\"><h1 class=\"text-4xl font-bold text-red-600 mb-4\">500</h1><p class=\"text-gray-600\">Server Encountered An Error</p><a href=\"/\" class=\"mt-4 inline-block px-4 py-2 bg-indigo-600 text-white rounded-lg\">Go Home</a></div>'), 500

    return app

app = create_app()

if __name__ == '__main__':
    # Auto-initialize database if not present
    db_file = os.path.join(Config.BASE_DIR, 'academia_portal.db')
    if not os.path.exists(db_file):
        print("Database not found. Seeding initial data...")
        from seed_data import seed_database
        seed_database()

    print("Starting Smart Academia-Industry Collaboration Portal on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
