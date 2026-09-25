from functools import wraps
from flask import Blueprint, request, jsonify, session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Config
from models import User, Student, StudentSkill, Job, Internship
from modules.ai_advisor.llm_engine import LLMCareerAdvisor

ai_bp = Blueprint('ai', __name__)
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(bind=engine)
advisor_engine = LLMCareerAdvisor()

def get_student_context(db, user_id):
    student = db.query(Student).filter_by(user_id=user_id).first()
    if not student:
        return {}
    skills_map = {ss.skill.name: (ss.verified_score or ss.proficiency_level) for ss in student.student_skills if ss.skill}
    readiness = student.assessments[-1].overall_readiness if student.assessments else 75.0
    return {
        'full_name': student.full_name,
        'degree': student.degree,
        'branch': student.branch,
        'cgpa': student.cgpa,
        'target_career': student.target_career,
        'skills': skills_map,
        'readiness': round(readiness, 1)
    }

@ai_bp.route('/api/ai/chat', methods=['POST'])
@ai_bp.route('/api/ai/advisor/chat', methods=['POST'])
def api_chat():
    data = request.get_json() or {}
    message = (data.get('message') or '').strip()
    if not message:
        return jsonify({'error': 'Message required'}), 400

    user_id = session.get('user_id')
    db = SessionLocal()
    try:
        student_ctx = get_student_context(db, user_id) if user_id else {}
        response_text = advisor_engine.chat(message, student_ctx)
        return jsonify({
            'success': True,
            'reply': response_text
        })
    finally:
        db.close()


@ai_bp.route('/api/ai/cover-letter', methods=['POST'])
def api_cover_letter():
    data = request.get_json() or {}
    job_id = data.get('job_id')
    internship_id = data.get('internship_id')

    user_id = session.get('user_id')
    db = SessionLocal()
    try:
        student_ctx = get_student_context(db, user_id) if user_id else {
            'full_name': 'Candidate',
            'degree': 'B.Tech',
            'branch': 'Computer Science',
            'cgpa': 8.5,
            'skills': {'Python': 85, 'SQL': 80}
        }

        opp_dict = {
            'title': 'Software Engineer',
            'company_name': 'Hiring Team',
            'required_skills': ['Python', 'SQL', 'Git']
        }

        if job_id:
            job = db.query(Job).filter_by(id=job_id).first()
            if job:
                opp_dict = {
                    'title': job.title,
                    'company_name': job.company.company_name if job.company else 'Organization',
                    'required_skills': [jrs.skill.name for jrs in job.required_skills if jrs.skill]
                }
        elif internship_id:
            intern = db.query(Internship).filter_by(id=internship_id).first()
            if intern:
                opp_dict = {
                    'title': intern.title,
                    'company_name': intern.company.company_name if intern.company else 'Organization',
                    'required_skills': [jrs.skill.name for jrs in intern.required_skills if jrs.skill]
                }

        if data.get('opportunity_title'):
            opp_dict['title'] = data['opportunity_title']
        if data.get('company_name'):
            opp_dict['company_name'] = data['company_name']
        if data.get('required_skills'):
            opp_dict['required_skills'] = data['required_skills']

        cover_letter = advisor_engine.generate_cover_letter(student_ctx, opp_dict)
        return jsonify({
            'success': True,
            'cover_letter': cover_letter
        })
    finally:
        db.close()


@ai_bp.route('/api/ai/extract-skills', methods=['POST'])
def api_extract_skills():
    data = request.get_json() or {}
    text = (data.get('text') or '').strip()
    if not text:
        return jsonify({'error': 'Text is required for skill extraction'}), 400

    extracted = advisor_engine.extract_skills_from_text(text)
    return jsonify({
        'success': True,
        'extracted_skills': extracted,
        'skills': [s['name'] for s in extracted],
        'count': len(extracted)
    })


@ai_bp.route('/api/ai/roadmap', methods=['POST'])
@ai_bp.route('/api/ai/learning-roadmap', methods=['POST'])
def api_roadmap():
    data = request.get_json() or {}
    missing_skills = data.get('missing_skills')
    if missing_skills and isinstance(missing_skills, list) and len(missing_skills) > 0:
        skill = missing_skills[0]
    else:
        skill = (data.get('skill') or 'Machine Learning').strip()
    target_role = (data.get('target_role') or '').strip()

    roadmap = advisor_engine.generate_learning_roadmap(skill, target_role)
    return jsonify({
        'success': True,
        'roadmap': roadmap
    })


@ai_bp.route('/api/ai/interview-prep', methods=['POST'])
def api_interview_prep():
    data = request.get_json() or {}
    job_title = (data.get('job_title') or 'Software Developer').strip()
    skills = data.get('required_skills') or ['Python', 'SQL', 'Git']

    questions = advisor_engine.generate_interview_questions(job_title, skills)
    return jsonify({
        'success': True,
        'questions': questions
    })
