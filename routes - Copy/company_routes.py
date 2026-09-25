import json
from functools import wraps
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Config
from models import (
    Company, Job, Internship, JobRequiredSkill, Skill,
    Application, Student, StudentSkill, TrainingProgram, MentorshipProgram, Notification
)
from modules.matching_engine.matching_engine import AIJobMatchingEngine

company_bp = Blueprint('company', __name__)
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(bind=engine)

def company_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'company':
            flash('Please log in with a company account to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


# ==========================================
# PAGE ROUTES (Member 3 Frontend Views)
# ==========================================

@company_bp.route('/company/dashboard')
@company_required
def dashboard():
    db = SessionLocal()
    try:
        company_id = session.get('profile_id')
        company = db.query(Company).filter_by(id=company_id).first()
        if not company:
            flash('Company profile not found', 'danger')
            return redirect(url_for('auth.login'))

        jobs = db.query(Job).filter_by(company_id=company.id).all()
        internships = db.query(Internship).filter_by(company_id=company.id).all()

        job_ids = [j.id for j in jobs]
        intern_ids = [i.id for i in internships]

        # All applications to this company's postings
        applications = db.query(Application).filter(
            (Application.job_id.in_(job_ids) if job_ids else False) |
            (Application.internship_id.in_(intern_ids) if intern_ids else False)
        ).order_by(Application.match_score.desc()).all()

        shortlisted_count = sum(1 for a in applications if a.status == 'Shortlisted')
        interview_count = sum(1 for a in applications if a.status == 'Interview')
        selected_count = sum(1 for a in applications if a.status == 'Selected')

        return render_template(
            'company/dashboard.html',
            company=company,
            jobs=jobs,
            internships=internships,
            applications=applications,
            shortlisted_count=shortlisted_count,
            interview_count=interview_count,
            selected_count=selected_count
        )
    finally:
        db.close()


@company_bp.route('/company/profile', methods=['GET', 'POST'])
@company_required
def profile():
    db = SessionLocal()
    try:
        company_id = session.get('profile_id')
        company = db.query(Company).filter_by(id=company_id).first()
        if request.method == 'POST':
            company.company_name = request.form.get('company_name', company.company_name)
            company.industry_type = request.form.get('industry_type', company.industry_type)
            company.website = request.form.get('website', company.website)
            company.location = request.form.get('location', company.location)
            company.description = request.form.get('description', company.description)
            db.commit()
            flash('Company profile updated successfully!', 'success')
            return redirect(url_for('company.profile'))

        return render_template('company/profile.html', company=company)
    finally:
        db.close()


@company_bp.route('/company/post-job', methods=['GET', 'POST'])
@company_required
def post_job():
    db = SessionLocal()
    try:
        company_id = session.get('profile_id')
        company = db.query(Company).filter_by(id=company_id).first()
        all_skills = db.query(Skill).all()

        if request.method == 'POST':
            post_type = request.form.get('posting_type', 'Job') # 'Job' or 'Internship'
            title = request.form.get('title', '').strip()
            desc = request.form.get('description', '').strip()
            location = request.form.get('location', 'Bengaluru / Hybrid').strip()
            selected_skills = request.form.getlist('skills') # skill names or IDs

            if not title or not desc:
                flash('Title and description are required', 'danger')
                return redirect(url_for('company.post_job'))

            if post_type == 'Job':
                job = Job(
                    company_id=company.id,
                    title=title,
                    job_type=request.form.get('job_type', 'Full-time'),
                    description=desc,
                    min_qualification=request.form.get('min_qualification', 'B.Tech / B.E'),
                    experience_years=int(request.form.get('experience_years', 0)),
                    location=location,
                    salary=request.form.get('salary', 'Competitive Market CTC'),
                    status='Open'
                )
                db.add(job)
                db.flush()

                for sk_id_or_name in selected_skills:
                    sk = db.query(Skill).filter((Skill.id == sk_id_or_name) | (Skill.name == sk_id_or_name)).first()
                    if sk:
                        db.add(JobRequiredSkill(job_id=job.id, skill_id=sk.id, min_proficiency=65.0))

                db.commit()
                flash(f'Job posting "{title}" published successfully!', 'success')
                return redirect(url_for('company.dashboard'))

            else: # Internship
                intern = Internship(
                    company_id=company.id,
                    title=title,
                    internship_type=request.form.get('internship_type', 'Summer Internship'),
                    description=desc,
                    duration_months=int(request.form.get('duration_months', 3)),
                    stipend=request.form.get('stipend', '₹ 20,000 / month'),
                    location=location,
                    status='Open'
                )
                db.add(intern)
                db.flush()

                for sk_id_or_name in selected_skills:
                    sk = db.query(Skill).filter((Skill.id == sk_id_or_name) | (Skill.name == sk_id_or_name)).first()
                    if sk:
                        db.add(JobRequiredSkill(internship_id=intern.id, skill_id=sk.id, min_proficiency=60.0))

                db.commit()
                flash(f'Internship posting "{title}" published successfully!', 'success')
                return redirect(url_for('company.dashboard'))

        return render_template('company/post_job.html', company=company, skills=all_skills)
    finally:
        db.close()


@company_bp.route('/company/applicants')
@company_required
def applicants():
    db = SessionLocal()
    try:
        company_id = session.get('profile_id')
        company = db.query(Company).filter_by(id=company_id).first()

        jobs = db.query(Job).filter_by(company_id=company.id).all()
        internships = db.query(Internship).filter_by(company_id=company.id).all()

        job_ids = [j.id for j in jobs]
        intern_ids = [i.id for i in internships]

        selected_job_id = request.args.get('job_id', type=int)
        selected_intern_id = request.args.get('intern_id', type=int)

        q = db.query(Application)
        if selected_job_id:
            q = q.filter_by(job_id=selected_job_id)
        elif selected_intern_id:
            q = q.filter_by(internship_id=selected_intern_id)
        else:
            q = q.filter(
                (Application.job_id.in_(job_ids) if job_ids else False) |
                (Application.internship_id.in_(intern_ids) if intern_ids else False)
            )

        apps = q.order_by(Application.match_score.desc()).all()

        # Detailed breakdown with AI matching details
        matching_engine = AIJobMatchingEngine()
        enriched_apps = []
        for a in apps:
            opp_skills = []
            opp_title = ""
            if a.job:
                opp_skills = [jrs.skill.name for jrs in a.job.required_skills if jrs.skill]
                opp_title = a.job.title
            elif a.internship:
                opp_skills = [jrs.skill.name for jrs in a.internship.required_skills if jrs.skill]
                opp_title = a.internship.title

            stu = a.student
            stu_skills_map = {ss.skill.name: (ss.verified_score or ss.proficiency_level) for ss in stu.student_skills if ss.skill} if stu else {}
            
            matched = [s for s in opp_skills if s.lower() in [k.lower() for k in stu_skills_map.keys()]]
            missing = [s for s in opp_skills if s.lower() not in [k.lower() for k in stu_skills_map.keys()]]

            enriched_apps.append({
                'application': a,
                'student': stu,
                'target_title': opp_title,
                'matched_skills': matched,
                'missing_skills': missing,
                'student_skills_map': stu_skills_map
            })

        return render_template(
            'company/applicants.html',
            company=company,
            jobs=jobs,
            internships=internships,
            enriched_apps=enriched_apps,
            selected_job_id=selected_job_id,
            selected_intern_id=selected_intern_id
        )
    finally:
        db.close()


@company_bp.route('/company/collaborations', methods=['GET', 'POST'])
@company_required
def collaborations():
    db = SessionLocal()
    try:
        company_id = session.get('profile_id')
        company = db.query(Company).filter_by(id=company_id).first()

        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            prog_type = request.form.get('program_type', 'Workshop')
            desc = request.form.get('description', '').strip()
            dur = request.form.get('duration', '4 Weeks')
            elig = request.form.get('eligibility', 'Open to Engineering Students & Faculty')
            link = request.form.get('registration_link', '')

            if title and desc:
                prog = TrainingProgram(
                    company_id=company.id,
                    title=title,
                    program_type=prog_type,
                    description=desc,
                    duration=dur,
                    eligibility=elig,
                    registration_link=link
                )
                db.add(prog)
                db.commit()
                flash(f'Industry program "{title}" created successfully!', 'success')
                return redirect(url_for('company.collaborations'))

        programs = db.query(TrainingProgram).all()
        mentorships = db.query(MentorshipProgram).filter_by(company_id=company.id).all()

        return render_template(
            'company/collaborations.html',
            company=company,
            programs=programs,
            mentorships=mentorships
        )
    finally:
        db.close()


# ==========================================
# REST API (Status Updates & Actions)
# ==========================================

@company_bp.route('/api/company/applications/<int:app_id>/status', methods=['POST'])
@company_required
def api_update_status(app_id):
    data = request.get_json() or {}
    new_status = data.get('status', '').strip()
    valid_statuses = ['Applied', 'Under Review', 'Shortlisted', 'Interview', 'Selected', 'Rejected']

    if new_status not in valid_statuses:
        return jsonify({'error': f'Invalid status. Must be one of {valid_statuses}'}), 400

    db = SessionLocal()
    try:
        app = db.query(Application).filter_by(id=app_id).first()
        if not app:
            return jsonify({'error': 'Application not found'}), 404

        app.status = new_status

        # Send automatic notification to student
        title_target = app.job.title if app.job else (app.internship.title if app.internship else 'Opportunity')
        db.add(Notification(
            user_id=app.student.user_id,
            title="Application Status Updated",
            message=f"Your application status for '{title_target}' has been updated to: '{new_status}'.",
            category="Application"
        ))

        db.commit()
        return jsonify({'success': True, 'new_status': new_status})
    finally:
        db.close()
