import json
from functools import wraps
from datetime import datetime
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Config
from models import (
    User, Student, Skill, StudentSkill, SkillAssessment,
    AssessmentQuestion, AssessmentAnswer, Certificate, Project,
    Job, Internship, Application, SkillMatch, Notification, CompanyFollow
)
from modules.ai_assessment.assessment_engine import AIAssessmentEngine
from modules.matching_engine.matching_engine import AIJobMatchingEngine

student_bp = Blueprint('student', __name__)
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(bind=engine)

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'student':
            flash('Please log in as a student to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


# ==========================================
# PAGE ROUTES (Member 2 Frontend Views)
# ==========================================

@student_bp.route('/student/dashboard')
@student_required
def dashboard():
    db = SessionLocal()
    try:
        student_id = session.get('profile_id')
        student = db.query(Student).filter_by(id=student_id).first()
        if not student:
            flash('Student record not found.', 'danger')
            return redirect(url_for('auth.login'))

        # Latest assessment
        latest_assessment = db.query(SkillAssessment).filter_by(student_id=student.id).order_by(SkillAssessment.completed_at.desc()).first()

        # Skills
        student_skills = db.query(StudentSkill).filter_by(student_id=student.id).all()
        strong_skills = [ss.skill.name for ss in student_skills if ss.status == 'Strong' and ss.skill]
        weak_skills = [ss.skill.name for ss in student_skills if ss.status == 'Weak' and ss.skill]
        missing_skills = [ss.skill.name for ss in student_skills if ss.status == 'Missing' and ss.skill]

        # Applications
        applications = db.query(Application).filter_by(student_id=student.id).order_by(Application.applied_at.desc()).limit(5).all()

        # Calculate live job & internship recommendations using Member 4 AI Matching Engine
        matching_engine = AIJobMatchingEngine()
        stu_dict = {
            'skills': {ss.skill.name: (ss.verified_score or ss.proficiency_level) for ss in student_skills if ss.skill},
            'degree': student.degree,
            'branch': student.branch,
            'cgpa': student.cgpa,
            'target_career': student.target_career,
            'location': student.location
        }

        jobs = db.query(Job).filter_by(status='Open').all()
        internships = db.query(Internship).filter_by(status='Open').all()

        opportunities = []
        for j in jobs:
            opportunities.append({
                'id': j.id,
                'title': j.title,
                'type': 'Job',
                'company_name': j.company.company_name if j.company else '',
                'location': j.location,
                'salary': j.salary,
                'min_qualification': j.min_qualification,
                'required_skills': [jrs.skill.name for jrs in j.required_skills if jrs.skill]
            })
        for i in internships:
            opportunities.append({
                'id': i.id,
                'title': i.title,
                'type': 'Internship',
                'company_name': i.company.company_name if i.company else '',
                'location': i.location,
                'stipend': i.stipend,
                'min_qualification': 'Open',
                'required_skills': [jrs.skill.name for jrs in i.required_skills if jrs.skill]
            })

        ranked_recs = matching_engine.rank_opportunities(stu_dict, opportunities)[:4]

        # Certificates and Projects
        certificates = db.query(Certificate).filter_by(student_id=student.id).all()
        projects = db.query(Project).filter_by(student_id=student.id).all()

        return render_template(
            'student/dashboard.html',
            student=student,
            assessment=latest_assessment,
            student_skills=student_skills,
            strong_skills=strong_skills,
            weak_skills=weak_skills,
            missing_skills=missing_skills,
            applications=applications,
            recommendations=ranked_recs,
            certificates=certificates,
            projects=projects
        )
    finally:
        db.close()


@student_bp.route('/student/profile', methods=['GET', 'POST'])
@student_required
def profile():
    db = SessionLocal()
    try:
        student_id = session.get('profile_id')
        student = db.query(Student).filter_by(id=student_id).first()
        if request.method == 'POST':
            student.full_name = request.form.get('full_name', student.full_name)
            student.degree = request.form.get('degree', student.degree)
            student.branch = request.form.get('branch', student.branch)
            student.graduation_year = int(request.form.get('graduation_year', student.graduation_year or 2026))
            student.cgpa = float(request.form.get('cgpa', student.cgpa or 8.0))
            student.target_career = request.form.get('target_career', student.target_career)
            student.location = request.form.get('location', student.location)
            student.bio = request.form.get('bio', student.bio)
            db.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('student.profile'))

        student_skills = db.query(StudentSkill).filter_by(student_id=student.id).all()
        all_skills = db.query(Skill).all()
        certificates = db.query(Certificate).filter_by(student_id=student.id).all()
        projects = db.query(Project).filter_by(student_id=student.id).all()

        return render_template(
            'student/profile.html',
            student=student,
            student_skills=student_skills,
            all_skills=all_skills,
            certificates=certificates,
            projects=projects
        )
    finally:
        db.close()


@student_bp.route('/student/assessment')
@student_required
def assessment():
    db = SessionLocal()
    try:
        student_id = session.get('profile_id')
        student = db.query(Student).filter_by(id=student_id).first()
        questions = db.query(AssessmentQuestion).all()
        latest_assessment = db.query(SkillAssessment).filter_by(student_id=student.id).order_by(SkillAssessment.completed_at.desc()).first()
        return render_template(
            'student/assessment.html',
            student=student,
            questions=questions,
            latest_assessment=latest_assessment
        )
    finally:
        db.close()


@student_bp.route('/student/jobs')
@student_required
def jobs():
    db = SessionLocal()
    try:
        student_id = session.get('profile_id')
        student = db.query(Student).filter_by(id=student_id).first()
        student_skills = db.query(StudentSkill).filter_by(student_id=student.id).all()

        matching_engine = AIJobMatchingEngine()
        stu_dict = {
            'skills': {ss.skill.name: (ss.verified_score or ss.proficiency_level) for ss in student_skills if ss.skill},
            'degree': student.degree,
            'branch': student.branch,
            'cgpa': student.cgpa,
            'target_career': student.target_career,
            'location': student.location
        }

        all_jobs = db.query(Job).filter_by(status='Open').all()
        all_internships = db.query(Internship).filter_by(status='Open').all()

        # Check existing applications & followed companies
        user_id = session.get('user_id')
        followed_company_ids = set()
        if user_id:
            followed_company_ids = {cf.company_id for cf in db.query(CompanyFollow).filter_by(user_id=user_id).all()}

        existing_applied_jobs = {a.job_id for a in db.query(Application).filter_by(student_id=student.id).all() if a.job_id}
        existing_applied_internships = {a.internship_id for a in db.query(Application).filter_by(student_id=student.id).all() if a.internship_id}

        opp_list = []
        for j in all_jobs:
            opp_list.append({
                'id': j.id,
                'title': j.title,
                'type': 'Job',
                'company_id': j.company_id,
                'company_name': j.company.company_name if j.company else 'Organization',
                'is_following': j.company_id in followed_company_ids if j.company_id else False,
                'location': j.location,
                'salary': j.salary,
                'description': j.description,
                'min_qualification': j.min_qualification,
                'experience_years': j.experience_years,
                'required_skills': [jrs.skill.name for jrs in j.required_skills if jrs.skill],
                'already_applied': j.id in existing_applied_jobs
            })
        for i in all_internships:
            opp_list.append({
                'id': i.id,
                'title': i.title,
                'type': 'Internship',
                'company_id': i.company_id,
                'company_name': i.company.company_name if i.company else 'Organization',
                'is_following': i.company_id in followed_company_ids if i.company_id else False,
                'location': i.location,
                'stipend': i.stipend,
                'description': i.description,
                'duration_months': i.duration_months,
                'min_qualification': 'Open to Pre-final & Final Years',
                'required_skills': [jrs.skill.name for jrs in i.required_skills if jrs.skill],
                'already_applied': i.id in existing_applied_internships
            })

        ranked_opportunities = []
        for opp in opp_list:
            match_res = matching_engine.calculate_match(stu_dict, opp)
            merged = {**opp, **match_res}
            ranked_opportunities.append(merged)

        ranked_opportunities.sort(key=lambda x: x['match_percentage'], reverse=True)

        return render_template('student/jobs.html', student=student, opportunities=ranked_opportunities)
    finally:
        db.close()


@student_bp.route('/student/applications')
@student_required
def applications():
    db = SessionLocal()
    try:
        student_id = session.get('profile_id')
        student = db.query(Student).filter_by(id=student_id).first()
        apps = db.query(Application).filter_by(student_id=student.id).order_by(Application.applied_at.desc()).all()
        return render_template('student/applications.html', student=student, applications=apps)
    finally:
        db.close()


@student_bp.route('/portfolio/<slug>')
def public_portfolio(slug):
    """Digital Student Portfolio accessible publicly or shared with companies."""
    db = SessionLocal()
    try:
        student = db.query(Student).filter_by(portfolio_slug=slug).first()
        if not student:
            return "Student portfolio not found.", 404

        latest_assessment = db.query(SkillAssessment).filter_by(student_id=student.id).order_by(SkillAssessment.completed_at.desc()).first()
        student_skills = db.query(StudentSkill).filter_by(student_id=student.id).all()
        certificates = db.query(Certificate).filter_by(student_id=student.id).all()
        projects = db.query(Project).filter_by(student_id=student.id).all()

        return render_template(
            'student/portfolio.html',
            student=student,
            assessment=latest_assessment,
            student_skills=student_skills,
            certificates=certificates,
            projects=projects,
            is_public_view=True
        )
    finally:
        db.close()


@student_bp.route('/student/portfolio')
@student_required
def student_portfolio_preview():
    db = SessionLocal()
    try:
        student_id = session.get('profile_id')
        student = db.query(Student).filter_by(id=student_id).first()
        return redirect(url_for('student.public_portfolio', slug=student.portfolio_slug))
    finally:
        db.close()


# ==========================================
# REST API ENDPOINTS (Member 6 Integration)
# ==========================================

@student_bp.route('/api/assessment/questions')
@student_required
def api_assessment_questions():
    db = SessionLocal()
    try:
        questions = db.query(AssessmentQuestion).all()
        return jsonify([q.to_dict(include_correct=False) for q in questions])
    finally:
        db.close()


@student_bp.route('/api/assessment/submit', methods=['POST'])
@student_required
def api_assessment_submit():
    """
    Submits answers, invokes Member 1 AI Assessment Engine,
    persists results to skill_assessments & updates student_skills.
    """
    data = request.get_json() or {}
    answers_map = data.get('answers', {}) # question_id -> selected_option

    db = SessionLocal()
    try:
        student_id = session.get('profile_id')
        student = db.query(Student).filter_by(id=student_id).first()
        if not student:
            return jsonify({'error': 'Student not found'}), 404

        questions = db.query(AssessmentQuestion).all()
        submissions = []
        for q in questions:
            qid_str = str(q.id)
            sel = answers_map.get(qid_str, '')
            submissions.append({
                'question_id': q.id,
                'skill': q.skill.name if q.skill else 'General',
                'category': q.category,
                'selected_option': sel,
                'correct_option': q.correct_option
            })

        # Run Member 1 AI Engine
        engine_eval = AIAssessmentEngine()
        result = engine_eval.evaluate_answers(submissions)

        # Persist Assessment
        assessment = SkillAssessment(
            student_id=student.id,
            technical_score=result['technical_score'],
            soft_skill_score=result['soft_skill_score'],
            aptitude_score=result['aptitude_score'],
            overall_readiness=result['overall_readiness'],
            strong_skills_json=json.dumps(result['strong_skills']),
            weak_skills_json=json.dumps(result['weak_skills']),
            missing_skills_json=json.dumps(result['missing_skills'])
        )
        db.add(assessment)
        db.flush()

        # Record answer log
        for ans in result['evaluated_answers']:
            db.add(AssessmentAnswer(
                assessment_id=assessment.id,
                question_id=ans['question_id'],
                selected_option=ans['selected_option'],
                is_correct=ans['is_correct']
            ))

        # Update or create student_skills based on AI results
        for skill_name, sk_data in result['skill_breakdown'].items():
            skill_obj = db.query(Skill).filter_by(name=skill_name).first()
            if skill_obj:
                score = sk_data['score']
                status = 'Strong' if score >= 70.0 else ('Weak' if score >= 40.0 else 'Missing')
                existing_ss = db.query(StudentSkill).filter_by(student_id=student.id, skill_id=skill_obj.id).first()
                if existing_ss:
                    existing_ss.verified_score = score
                    existing_ss.proficiency_level = score
                    existing_ss.status = status
                else:
                    db.add(StudentSkill(
                        student_id=student.id,
                        skill_id=skill_obj.id,
                        proficiency_level=score,
                        verified_score=score,
                        status=status
                    ))

        # Create system notification
        db.add(Notification(
            user_id=student.user_id,
            title="AI Skill Assessment Completed",
            message=f"Your assessment has been evaluated! Overall Readiness: {result['overall_readiness']}%. Check your updated skill profile.",
            category="Assessment"
        ))

        db.commit()
        return jsonify({
            'success': True,
            'assessment_id': assessment.id,
            'result': result
        }), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@student_bp.route('/api/applications/apply', methods=['POST'])
@student_required
def api_apply_opportunity():
    data = request.get_json() or {}
    job_id = data.get('job_id')
    internship_id = data.get('internship_id')
    cover_note = data.get('cover_note', '')

    db = SessionLocal()
    try:
        student_id = session.get('profile_id')
        student = db.query(Student).filter_by(id=student_id).first()

        # Check existing
        q = db.query(Application).filter_by(student_id=student.id)
        if job_id:
            q = q.filter_by(job_id=job_id)
        elif internship_id:
            q = q.filter_by(internship_id=internship_id)

        if q.first():
            return jsonify({'error': 'You have already applied for this opportunity'}), 400

        # Calculate AI Match Score using Member 4 Engine
        matching_engine = AIJobMatchingEngine()
        student_skills = db.query(StudentSkill).filter_by(student_id=student.id).all()
        stu_dict = {
            'skills': {ss.skill.name: (ss.verified_score or ss.proficiency_level) for ss in student_skills if ss.skill},
            'degree': student.degree,
            'branch': student.branch,
            'cgpa': student.cgpa,
            'target_career': student.target_career,
            'location': student.location
        }

        target_company_user_id = None
        opp_title = ""
        if job_id:
            job = db.query(Job).filter_by(id=job_id).first()
            opp_dict = {
                'id': job.id,
                'title': job.title,
                'type': 'Job',
                'min_qualification': job.min_qualification,
                'required_skills': [jrs.skill.name for jrs in job.required_skills if jrs.skill],
                'location': job.location
            }
            target_company_user_id = job.company.user_id if job.company else None
            opp_title = job.title
        else:
            intern = db.query(Internship).filter_by(id=internship_id).first()
            opp_dict = {
                'id': intern.id,
                'title': intern.title,
                'type': 'Internship',
                'min_qualification': 'Open',
                'required_skills': [jrs.skill.name for jrs in intern.required_skills if jrs.skill],
                'location': intern.location
            }
            target_company_user_id = intern.company.user_id if intern.company else None
            opp_title = intern.title

        match_res = matching_engine.calculate_match(stu_dict, opp_dict)
        match_score = match_res['match_percentage']

        app = Application(
            student_id=student.id,
            job_id=job_id,
            internship_id=internship_id,
            match_score=match_score,
            status='Applied',
            cover_note=cover_note
        )
        db.add(app)

        # Notify company
        if target_company_user_id:
            db.add(Notification(
                user_id=target_company_user_id,
                title="New Applicant",
                message=f"{student.full_name} ({match_score}% Match) applied for '{opp_title}'.",
                category="Application"
            ))

        db.commit()
        return jsonify({
            'success': True,
            'application_id': app.id,
            'match_score': match_score,
            'message': f'Application successfully submitted with AI Match Score of {match_score}%!'
        })
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@student_bp.route('/api/student/skills/add', methods=['POST'])
@student_required
def api_add_skill():
    data = request.get_json() or {}
    skill_name = data.get('skill_name', '').strip()
    proficiency = float(data.get('proficiency', 50.0))

    if not skill_name:
        return jsonify({'error': 'Skill name required'}), 400

    db = SessionLocal()
    try:
        student_id = session.get('profile_id')
        skill = db.query(Skill).filter_by(name=skill_name).first()
        if not skill:
            skill = Skill(name=skill_name, category='Technical')
            db.add(skill)
            db.flush()

        status = 'Strong' if proficiency >= 70 else ('Weak' if proficiency >= 40 else 'Missing')
        ss = db.query(StudentSkill).filter_by(student_id=student_id, skill_id=skill.id).first()
        if ss:
            ss.proficiency_level = proficiency
            ss.status = status
        else:
            ss = StudentSkill(
                student_id=student_id,
                skill_id=skill.id,
                proficiency_level=proficiency,
                verified_score=proficiency,
                status=status
            )
            db.add(ss)

        db.commit()
        return jsonify({'success': True, 'skill': ss.to_dict()})
    finally:
        db.close()


@student_bp.route('/api/student/projects/add', methods=['POST'])
@student_required
def api_add_project():
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    desc = data.get('description', '').strip()
    tech = data.get('tech_stack', '').strip()
    github = data.get('github_url', '').strip()
    live = data.get('live_url', '').strip()

    if not title:
        return jsonify({'error': 'Project title is required'}), 400

    db = SessionLocal()
    try:
        student_id = session.get('profile_id')
        p = Project(
            student_id=student_id,
            title=title,
            description=desc,
            tech_stack=tech,
            github_url=github,
            live_url=live
        )
        db.add(p)
        db.commit()
        return jsonify({'success': True, 'project': p.to_dict()})
    finally:
        db.close()


@student_bp.route('/api/student/certificates/add', methods=['POST'])
@student_required
def api_add_certificate():
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    org = data.get('issuing_org', '').strip()
    date_val = data.get('issue_date', '').strip()
    url_val = data.get('credential_url', '').strip()

    if not title or not org:
        return jsonify({'error': 'Title and Issuing Organization are required'}), 400

    db = SessionLocal()
    try:
        student_id = session.get('profile_id')
        c = Certificate(
            student_id=student_id,
            title=title,
            issuing_org=org,
            issue_date=date_val,
            credential_url=url_val,
            status='Verified'
        )
        db.add(c)
        db.commit()
        return jsonify({'success': True, 'certificate': c.to_dict()})
    finally:
        db.close()
