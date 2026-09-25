import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    role = Column(String(30), nullable=False)  # 'student', 'company', 'college', 'admin'
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    student_profile = relationship('Student', back_populates='user', uselist=False, cascade='all, delete-orphan')
    company_profile = relationship('Company', back_populates='user', uselist=False, cascade='all, delete-orphan')
    college_profile = relationship('College', back_populates='user', uselist=False, cascade='all, delete-orphan')
    notifications = relationship('Notification', back_populates='user', cascade='all, delete-orphan')
    sent_messages = relationship('Message', foreign_keys='Message.sender_id', back_populates='sender', cascade='all, delete-orphan')
    received_messages = relationship('Message', foreign_keys='Message.recipient_id', back_populates='recipient', cascade='all, delete-orphan')
    followed_companies = relationship('CompanyFollow', back_populates='user', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }


class College(Base):
    __tablename__ = 'colleges'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    college_name = Column(String(200), nullable=False)
    code = Column(String(50), nullable=True)
    location = Column(String(120), nullable=True)
    contact_email = Column(String(120), nullable=True)
    website = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='college_profile')
    students = relationship('Student', back_populates='college')
    training_programs = relationship('TrainingProgram', back_populates='college')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'college_name': self.college_name,
            'code': self.code,
            'location': self.location,
            'contact_email': self.contact_email,
            'website': self.website
        }


class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    college_id = Column(Integer, ForeignKey('colleges.id'), nullable=True)
    full_name = Column(String(120), nullable=False)
    roll_no = Column(String(50), nullable=True)
    degree = Column(String(100), default='B.Tech')
    branch = Column(String(100), default='Computer Science')
    graduation_year = Column(Integer, default=2026)
    cgpa = Column(Float, default=8.0)
    bio = Column(Text, nullable=True)
    target_career = Column(String(120), default='Software Engineer')
    location = Column(String(100), default='Bengaluru, India')
    portfolio_slug = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='student_profile')
    college = relationship('College', back_populates='students')
    student_skills = relationship('StudentSkill', back_populates='student', cascade='all, delete-orphan')
    assessments = relationship('SkillAssessment', back_populates='student', cascade='all, delete-orphan')
    certificates = relationship('Certificate', back_populates='student', cascade='all, delete-orphan')
    projects = relationship('Project', back_populates='student', cascade='all, delete-orphan')
    applications = relationship('Application', back_populates='student', cascade='all, delete-orphan')
    skill_matches = relationship('SkillMatch', back_populates='student', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.full_name,
            'college_id': self.college_id,
            'college_name': self.college.college_name if self.college else 'Independent / Autonomous',
            'roll_no': self.roll_no,
            'degree': self.degree,
            'branch': self.branch,
            'graduation_year': self.graduation_year,
            'cgpa': self.cgpa,
            'bio': self.bio,
            'target_career': self.target_career,
            'location': self.location,
            'portfolio_slug': self.portfolio_slug
        }


class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    company_name = Column(String(150), nullable=False)
    industry_type = Column(String(100), default='Information Technology')
    website = Column(String(255), nullable=True)
    location = Column(String(120), default='Bengaluru, India')
    description = Column(Text, nullable=True)
    verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='company_profile')
    jobs = relationship('Job', back_populates='company', cascade='all, delete-orphan')
    internships = relationship('Internship', back_populates='company', cascade='all, delete-orphan')
    training_programs = relationship('TrainingProgram', back_populates='company', cascade='all, delete-orphan')
    mentorship_programs = relationship('MentorshipProgram', back_populates='company', cascade='all, delete-orphan')
    followers = relationship('CompanyFollow', back_populates='company', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'company_name': self.company_name,
            'industry_type': self.industry_type,
            'website': self.website,
            'location': self.location,
            'description': self.description,
            'verified': self.verified
        }


class Skill(Base):
    __tablename__ = 'skills'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(50), default='Technical')  # 'Technical', 'Soft Skills', 'Aptitude', 'Cloud'
    description = Column(Text, nullable=True)

    student_skills = relationship('StudentSkill', back_populates='skill', cascade='all, delete-orphan')
    questions = relationship('AssessmentQuestion', back_populates='skill')
    required_in_jobs = relationship('JobRequiredSkill', back_populates='skill', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description
        }


class StudentSkill(Base):
    __tablename__ = 'student_skills'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    skill_id = Column(Integer, ForeignKey('skills.id'), nullable=False)
    proficiency_level = Column(Float, default=50.0)  # Self/estimated 0-100
    verified_score = Column(Float, default=0.0)      # AI assessment verified score
    status = Column(String(30), default='Weak')      # 'Strong' (>=70), 'Weak' (40-69), 'Missing' (<40)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = relationship('Student', back_populates='student_skills')
    skill = relationship('Skill', back_populates='student_skills')

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'skill_id': self.skill_id,
            'skill_name': self.skill.name if self.skill else None,
            'category': self.skill.category if self.skill else None,
            'proficiency_level': self.proficiency_level,
            'verified_score': self.verified_score,
            'status': self.status
        }


class SkillAssessment(Base):
    __tablename__ = 'skill_assessments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    technical_score = Column(Float, default=0.0)
    soft_skill_score = Column(Float, default=0.0)
    aptitude_score = Column(Float, default=0.0)
    overall_readiness = Column(Float, default=0.0)
    strong_skills_json = Column(Text, default='[]')
    weak_skills_json = Column(Text, default='[]')
    missing_skills_json = Column(Text, default='[]')
    completed_at = Column(DateTime, default=datetime.utcnow)

    student = relationship('Student', back_populates='assessments')
    answers = relationship('AssessmentAnswer', back_populates='assessment', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'technical_score': round(self.technical_score, 1),
            'soft_skill_score': round(self.soft_skill_score, 1),
            'aptitude_score': round(self.aptitude_score, 1),
            'overall_readiness': round(self.overall_readiness, 1),
            'strong_skills': json.loads(self.strong_skills_json or '[]'),
            'weak_skills': json.loads(self.weak_skills_json or '[]'),
            'missing_skills': json.loads(self.missing_skills_json or '[]'),
            'completed_at': self.completed_at.strftime('%Y-%m-%d %H:%M') if self.completed_at else None
        }


class AssessmentQuestion(Base):
    __tablename__ = 'assessment_questions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    skill_id = Column(Integer, ForeignKey('skills.id'), nullable=True)
    category = Column(String(50), default='Technical')  # 'Technical', 'Soft Skills', 'Aptitude'
    question_text = Column(Text, nullable=False)
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=False)
    option_d = Column(Text, nullable=False)
    correct_option = Column(String(5), nullable=False)  # 'A', 'B', 'C', 'D'
    difficulty = Column(String(20), default='Intermediate')  # 'Beginner', 'Intermediate', 'Advanced'

    skill = relationship('Skill', back_populates='questions')
    answers = relationship('AssessmentAnswer', back_populates='question')

    def to_dict(self, include_correct=False):
        d = {
            'id': self.id,
            'skill_id': self.skill_id,
            'skill_name': self.skill.name if self.skill else None,
            'category': self.category,
            'question_text': self.question_text,
            'options': {
                'A': self.option_a,
                'B': self.option_b,
                'C': self.option_c,
                'D': self.option_d
            },
            'difficulty': self.difficulty
        }
        if include_correct:
            d['correct_option'] = self.correct_option
        return d


class AssessmentAnswer(Base):
    __tablename__ = 'assessment_answers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    assessment_id = Column(Integer, ForeignKey('skill_assessments.id'), nullable=False)
    question_id = Column(Integer, ForeignKey('assessment_questions.id'), nullable=False)
    selected_option = Column(String(5), nullable=False)
    is_correct = Column(Boolean, default=False)

    assessment = relationship('SkillAssessment', back_populates='answers')
    question = relationship('AssessmentQuestion', back_populates='answers')


class Certificate(Base):
    __tablename__ = 'certificates'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    title = Column(String(200), nullable=False)
    issuing_org = Column(String(150), nullable=False)
    issue_date = Column(String(50), nullable=True)
    credential_url = Column(String(255), nullable=True)
    status = Column(String(30), default='Verified')  # 'Verified', 'Pending', 'Rejected'
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship('Student', back_populates='certificates')

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'title': self.title,
            'issuing_org': self.issuing_org,
            'issue_date': self.issue_date,
            'credential_url': self.credential_url,
            'status': self.status
        }


class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    tech_stack = Column(String(255), nullable=True)
    github_url = Column(String(255), nullable=True)
    live_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship('Student', back_populates='projects')

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'title': self.title,
            'description': self.description,
            'tech_stack': self.tech_stack,
            'github_url': self.github_url,
            'live_url': self.live_url
        }


class Job(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    title = Column(String(200), nullable=False)
    job_type = Column(String(50), default='Full-time')  # 'Full-time', 'Part-time', 'Apprenticeship'
    description = Column(Text, nullable=False)
    min_qualification = Column(String(100), default='B.Tech / B.E / BCA')
    experience_years = Column(Integer, default=0)
    location = Column(String(120), default='Bengaluru / Hybrid')
    salary = Column(String(100), default='₹ 6,00,000 - ₹ 10,00,000 P.A.')
    status = Column(String(30), default='Open')  # 'Open', 'Closed'
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship('Company', back_populates='jobs')
    required_skills = relationship('JobRequiredSkill', back_populates='job', cascade='all, delete-orphan')
    applications = relationship('Application', back_populates='job', cascade='all, delete-orphan')
    skill_matches = relationship('SkillMatch', back_populates='job', cascade='all, delete-orphan')

    def to_dict(self):
        skills = [jrs.skill.name for jrs in self.required_skills if jrs.skill]
        return {
            'id': self.id,
            'company_id': self.company_id,
            'company_name': self.company.company_name if self.company else None,
            'company_logo': 'briefcase',
            'title': self.title,
            'job_type': self.job_type,
            'description': self.description,
            'min_qualification': self.min_qualification,
            'experience_years': self.experience_years,
            'location': self.location,
            'salary': self.salary,
            'status': self.status,
            'required_skills': skills,
            'created_at': self.created_at.strftime('%b %d, %Y') if self.created_at else None
        }


class Internship(Base):
    __tablename__ = 'internships'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    title = Column(String(200), nullable=False)
    internship_type = Column(String(50), default='Summer Internship')  # 'Summer', 'Winter', 'Apprenticeship'
    description = Column(Text, nullable=False)
    duration_months = Column(Integer, default=3)
    stipend = Column(String(100), default='₹ 25,000 / month')
    location = Column(String(120), default='Remote / Bengaluru')
    status = Column(String(30), default='Open')  # 'Open', 'Closed'
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship('Company', back_populates='internships')
    required_skills = relationship('JobRequiredSkill', back_populates='internship', cascade='all, delete-orphan')
    applications = relationship('Application', back_populates='internship', cascade='all, delete-orphan')
    skill_matches = relationship('SkillMatch', back_populates='internship', cascade='all, delete-orphan')

    def to_dict(self):
        skills = [jrs.skill.name for jrs in self.required_skills if jrs.skill]
        return {
            'id': self.id,
            'company_id': self.company_id,
            'company_name': self.company.company_name if self.company else None,
            'title': self.title,
            'internship_type': self.internship_type,
            'description': self.description,
            'duration_months': self.duration_months,
            'stipend': self.stipend,
            'location': self.location,
            'status': self.status,
            'required_skills': skills,
            'created_at': self.created_at.strftime('%b %d, %Y') if self.created_at else None
        }


class JobRequiredSkill(Base):
    __tablename__ = 'job_required_skills'

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=True)
    internship_id = Column(Integer, ForeignKey('internships.id'), nullable=True)
    skill_id = Column(Integer, ForeignKey('skills.id'), nullable=False)
    importance_weight = Column(Float, default=1.0)
    min_proficiency = Column(Float, default=60.0)

    job = relationship('Job', back_populates='required_skills')
    internship = relationship('Internship', back_populates='required_skills')
    skill = relationship('Skill', back_populates='required_in_jobs')


class Application(Base):
    __tablename__ = 'applications'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=True)
    internship_id = Column(Integer, ForeignKey('internships.id'), nullable=True)
    match_score = Column(Float, default=0.0)
    status = Column(String(30), default='Applied')  # 'Applied', 'Under Review', 'Shortlisted', 'Interview', 'Selected', 'Rejected'
    cover_note = Column(Text, nullable=True)
    applied_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = relationship('Student', back_populates='applications')
    job = relationship('Job', back_populates='applications')
    internship = relationship('Internship', back_populates='applications')

    def to_dict(self):
        target_title = self.job.title if self.job else (self.internship.title if self.internship else 'Opportunity')
        company_name = self.job.company.company_name if self.job and self.job.company else (
            self.internship.company.company_name if self.internship and self.internship.company else 'Organization'
        )
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.full_name if self.student else None,
            'student_roll': self.student.roll_no if self.student else None,
            'student_degree': self.student.degree if self.student else None,
            'student_branch': self.student.branch if self.student else None,
            'student_cgpa': self.student.cgpa if self.student else None,
            'student_slug': self.student.portfolio_slug if self.student else None,
            'job_id': self.job_id,
            'internship_id': self.internship_id,
            'type': 'Job' if self.job_id else 'Internship',
            'title': target_title,
            'company_name': company_name,
            'match_score': round(self.match_score, 1),
            'status': self.status,
            'applied_at': self.applied_at.strftime('%b %d, %Y') if self.applied_at else None
        }


class SkillMatch(Base):
    __tablename__ = 'skill_matches'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=True)
    internship_id = Column(Integer, ForeignKey('internships.id'), nullable=True)
    match_percentage = Column(Float, default=0.0)
    matched_skills_json = Column(Text, default='[]')
    missing_skills_json = Column(Text, default='[]')
    explanation = Column(Text, nullable=True)
    calculated_at = Column(DateTime, default=datetime.utcnow)

    student = relationship('Student', back_populates='skill_matches')
    job = relationship('Job', back_populates='skill_matches')
    internship = relationship('Internship', back_populates='skill_matches')

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'job_id': self.job_id,
            'internship_id': self.internship_id,
            'match_percentage': round(self.match_percentage, 1),
            'matched_skills': json.loads(self.matched_skills_json or '[]'),
            'missing_skills': json.loads(self.missing_skills_json or '[]'),
            'explanation': self.explanation,
            'calculated_at': self.calculated_at.isoformat() if self.calculated_at else None
        }


class TrainingProgram(Base):
    __tablename__ = 'training_programs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True)
    college_id = Column(Integer, ForeignKey('colleges.id'), nullable=True)
    title = Column(String(200), nullable=False)
    program_type = Column(String(50), default='Workshop')  # 'Training', 'Certification', 'Workshop', 'FDP', 'Live Project'
    description = Column(Text, nullable=False)
    duration = Column(String(100), default='4 Weeks')
    eligibility = Column(String(200), default='Open to all pre-final & final year students')
    registration_link = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship('Company', back_populates='training_programs')
    college = relationship('College', back_populates='training_programs')

    def to_dict(self):
        host = self.company.company_name if self.company else (
            self.college.college_name if self.college else 'Industry-Academia Board'
        )
        return {
            'id': self.id,
            'title': self.title,
            'program_type': self.program_type,
            'host': host,
            'description': self.description,
            'duration': self.duration,
            'eligibility': self.eligibility,
            'registration_link': self.registration_link,
            'created_at': self.created_at.strftime('%b %d, %Y') if self.created_at else None
        }


class MentorshipProgram(Base):
    __tablename__ = 'mentorship_programs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    mentor_name = Column(String(120), nullable=False)
    domain = Column(String(120), default='AI / Data Science')
    description = Column(Text, nullable=True)
    sessions_count = Column(Integer, default=6)
    contact_email = Column(String(120), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship('Company', back_populates='mentorship_programs')

    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company.company_name if self.company else None,
            'mentor_name': self.mentor_name,
            'domain': self.domain,
            'description': self.description,
            'sessions_count': self.sessions_count,
            'contact_email': self.contact_email
        }


class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    category = Column(String(50), default='System')  # 'JobMatch', 'Internship', 'Assessment', 'Application'
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='notifications')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'category': self.category,
            'is_read': self.is_read,
            'time_ago': self.created_at.strftime('%b %d, %H:%M') if self.created_at else ''
        }


class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    recipient_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    sender = relationship('User', foreign_keys=[sender_id], back_populates='sent_messages')
    recipient = relationship('User', foreign_keys=[recipient_id], back_populates='received_messages')

    def to_dict(self):
        s_name = 'User'
        if self.sender:
            if self.sender.student_profile:
                s_name = self.sender.student_profile.full_name
            elif self.sender.company_profile:
                s_name = self.sender.company_profile.company_name
            elif self.sender.college_profile:
                s_name = self.sender.college_profile.college_name
            elif self.sender.role == 'admin':
                s_name = 'System Administrator'

        r_name = 'User'
        if self.recipient:
            if self.recipient.student_profile:
                r_name = self.recipient.student_profile.full_name
            elif self.recipient.company_profile:
                r_name = self.recipient.company_profile.company_name
            elif self.recipient.college_profile:
                r_name = self.recipient.college_profile.college_name

        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'recipient_id': self.recipient_id,
            'sender_name': s_name,
            'recipient_name': r_name,
            'sender_role': self.sender.role if self.sender else 'user',
            'content': self.content,
            'is_read': self.is_read,
            'created_at': self.created_at.strftime('%b %d, %H:%M') if self.created_at else ''
        }


class CompanyFollow(Base):
    __tablename__ = 'company_follows'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='followed_companies')
    company = relationship('Company', back_populates='followers')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'company_id': self.company_id,
            'company_name': self.company.company_name if self.company else None,
            'created_at': self.created_at.strftime('%b %d, %Y') if self.created_at else ''
        }

