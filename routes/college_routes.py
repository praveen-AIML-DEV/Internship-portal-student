from functools import wraps
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from config import Config
from models import (
    College, Student, StudentSkill, Skill, SkillAssessment,
    Job, Internship, JobRequiredSkill, Application, TrainingProgram
)

college_bp = Blueprint('college', __name__)
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(bind=engine)

def college_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'college':
            flash('Please log in with an institution account to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


# ==========================================
# PAGE ROUTES (Member 5 Frontend Views)
# ==========================================

@college_bp.route('/college/dashboard')
@college_required
def dashboard():
    db = SessionLocal()
    try:
        college_id = session.get('profile_id')
        college = db.query(College).filter_by(id=college_id).first()
        if not college:
            flash('College profile not found.', 'danger')
            return redirect(url_for('auth.login'))

        # 1. Student Analytics
        students = db.query(Student).filter((Student.college_id == college.id) | (Student.college_id == None)).all()
        total_students = len(students)
        stu_ids = [s.id for s in students]

        # Assessed students & average skill readiness
        assessments = db.query(SkillAssessment).filter(SkillAssessment.student_id.in_(stu_ids)).all() if stu_ids else []
        assessed_student_ids = set(a.student_id for a in assessments)
        assessed_count = len(assessed_student_ids)

        avg_score = round(sum(a.overall_readiness for a in assessments) / max(1, len(assessments)), 1) if assessments else 0.0
        placement_ready = sum(1 for a in assessments if a.overall_readiness >= 70.0)

        # Internship participation
        internship_apps = db.query(Application).filter(
            Application.student_id.in_(stu_ids),
            Application.internship_id != None
        ).all() if stu_ids else []
        internship_participating = len(set(a.student_id for a in internship_apps))

        # 2. Skill Analytics (Average Score per Skill)
        skill_averages = {}
        all_skills = db.query(Skill).all()
        for sk in all_skills:
            scores = db.query(StudentSkill.verified_score).filter(
                StudentSkill.student_id.in_(stu_ids),
                StudentSkill.skill_id == sk.id,
                StudentSkill.verified_score > 0
            ).all() if stu_ids else []
            if scores:
                avg = round(sum(s[0] for s in scores) / len(scores), 1)
                skill_averages[sk.name] = avg

        # Default chart fallback if fresh
        chart_skills = ['Python', 'Java', 'SQL', 'Machine Learning', 'Cloud Computing', 'Communication']
        skill_chart_data = {
            'labels': chart_skills,
            'scores': [skill_averages.get(k, 45.0) for k in chart_skills]
        }

        # 3. Skill Gap Analysis (Most Missing Skills)
        missing_skill_counts = {}
        for ss in db.query(StudentSkill).filter(StudentSkill.student_id.in_(stu_ids), StudentSkill.status == 'Missing').all() if stu_ids else []:
            if ss.skill:
                missing_skill_counts[ss.skill.name] = missing_skill_counts.get(ss.skill.name, 0) + 1

        # Fallback realistic top missing skills for demonstration
        if not missing_skill_counts:
            missing_skill_counts = {
                'Cloud Computing': 4,
                'Machine Learning': 3,
                'Cybersecurity': 3,
                'Data Analytics': 2,
                'Communication': 1
            }

        sorted_missing = sorted(missing_skill_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        # 4. Industry Demand Analysis (Aggregated from active Jobs & Internships)
        industry_skill_counts = {}
        for jrs in db.query(JobRequiredSkill).all():
            if jrs.skill:
                industry_skill_counts[jrs.skill.name] = industry_skill_counts.get(jrs.skill.name, 0) + 1

        # Calculate Demand Level: High (>=3), Medium (>=1), Low
        industry_demand = []
        for sk_name, count in sorted(industry_skill_counts.items(), key=lambda x: x[1], reverse=True):
            level = 'High' if count >= 3 else ('Medium' if count >= 2 else 'Growing')
            badge_class = 'bg-red-100 text-red-800' if level == 'High' else ('bg-blue-100 text-blue-800' if level == 'Medium' else 'bg-green-100 text-green-800')
            industry_demand.append({
                'skill': sk_name,
                'count': count,
                'level': level,
                'badge_class': badge_class
            })

        return render_template(
            'college/dashboard.html',
            college=college,
            total_students=total_students,
            assessed_count=assessed_count,
            avg_score=avg_score,
            placement_ready=placement_ready,
            internship_participating=internship_participating,
            skill_chart_data=skill_chart_data,
            top_missing_skills=sorted_missing,
            industry_demand=industry_demand
        )
    finally:
        db.close()


@college_bp.route('/college/students')
@college_required
def students_list():
    db = SessionLocal()
    try:
        college_id = session.get('profile_id')
        college = db.query(College).filter_by(id=college_id).first()

        students = db.query(Student).filter((Student.college_id == college.id) | (Student.college_id == None)).all()
        student_records = []

        for s in students:
            assessment = db.query(SkillAssessment).filter_by(student_id=s.id).order_by(SkillAssessment.completed_at.desc()).first()
            skills = db.query(StudentSkill).filter_by(student_id=s.id).all()
            strong = [ss.skill.name for ss in skills if ss.status == 'Strong' and ss.skill]
            missing = [ss.skill.name for ss in skills if ss.status == 'Missing' and ss.skill]

            readiness = assessment.overall_readiness if assessment else (s.cgpa * 10.0)
            status_tag = 'Placement Ready' if readiness >= 70.0 else ('Needs Training' if readiness >= 40.0 else 'High Gap')

            student_records.append({
                'student': s,
                'readiness': round(readiness, 1),
                'status_tag': status_tag,
                'strong_skills': strong,
                'missing_skills': missing,
                'assessment_completed': assessment is not None
            })

        return render_template('college/students.html', college=college, students=student_records)
    finally:
        db.close()


@college_bp.route('/college/collaboration')
@college_required
def collaboration():
    db = SessionLocal()
    try:
        college_id = session.get('profile_id')
        college = db.query(College).filter_by(id=college_id).first()
        programs = db.query(TrainingProgram).all()

        return render_template('college/collaboration.html', college=college, programs=programs)
    finally:
        db.close()


# JSON REST API
@college_bp.route('/api/college/analytics')
@college_required
def api_analytics():
    db = SessionLocal()
    try:
        college_id = session.get('profile_id')
        students = db.query(Student).all()
        total_students = len(students)
        stu_ids = [s.id for s in students]

        assessments = db.query(SkillAssessment).all()
        avg_score = round(sum(a.overall_readiness for a in assessments) / max(1, len(assessments)), 1) if assessments else 0.0

        return jsonify({
            'total_students': total_students,
            'assessed_students': len(assessments),
            'average_skill_score': avg_score,
            'placement_ready_students': sum(1 for a in assessments if a.overall_readiness >= 70)
        })
    finally:
        db.close()
