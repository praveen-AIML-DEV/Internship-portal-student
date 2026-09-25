import os
import json
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Config
from models import (
    Base, User, Student, Company, College, Skill, StudentSkill,
    SkillAssessment, AssessmentQuestion, AssessmentAnswer,
    Certificate, Project, Job, Internship, JobRequiredSkill,
    Application, SkillMatch, TrainingProgram, MentorshipProgram, Notification
)

def seed_database():
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    print("Populating initial database data...")

    # 1. Skills
    skills_data = [
        ("Python", "Technical", "High-level programming language for web, data, and AI"),
        ("SQL", "Technical", "Relational database querying and management"),
        ("Machine Learning", "Technical", "Statistical modeling, predictive algorithms, and neural networks"),
        ("Cloud Computing", "Technical", "AWS, Azure, and distributed cloud architecture"),
        ("Data Structures", "Technical", "Core algorithms, trees, graphs, and algorithmic complexity"),
        ("Java", "Technical", "Enterprise OOP language and backend system development"),
        ("React", "Technical", "Modern frontend component library and state management"),
        ("Git", "Technical", "Version control, branching workflows, and collaborative development"),
        ("Cybersecurity", "Technical", "Network defense, vulnerability assessment, and secure coding"),
        ("Communication", "Soft Skills", "Verbal clarity, cross-functional collaboration, and technical writing"),
        ("Teamwork", "Soft Skills", "Agile participation, conflict resolution, and peer review"),
        ("Quantitative Aptitude", "Aptitude", "Mathematical problem solving, numerical ability, and speed calculations"),
        ("Logical Reasoning", "Aptitude", "Analytical deductions, pattern recognition, and critical reasoning")
    ]

    skill_map = {}
    for name, cat, desc in skills_data:
        s = Skill(name=name, category=cat, description=desc)
        session.add(s)
        session.flush()
        skill_map[name] = s

    # 2. Questions from question_bank.json
    q_bank_path = os.path.join(Config.BASE_DIR, "modules", "ai_assessment", "question_bank.json")
    if os.path.exists(q_bank_path):
        with open(q_bank_path, "r", encoding="utf-8-sig") as f:
            q_list = json.load(f)
            for q_item in q_list:
                sk_name = q_item.get("skill")
                sk_obj = skill_map.get(sk_name)
                aq = AssessmentQuestion(
                    skill_id=sk_obj.id if sk_obj else None,
                    category=q_item.get("category", "Technical"),
                    question_text=q_item.get("question"),
                    option_a=q_item["options"]["A"],
                    option_b=q_item["options"]["B"],
                    option_c=q_item["options"]["C"],
                    option_d=q_item["options"]["D"],
                    correct_option=q_item.get("correct", "A"),
                    difficulty=q_item.get("difficulty", "Intermediate")
                )
                session.add(aq)

    # 3. Users: Admin, College, Company, Students
    # Admin
    admin_user = User(email="admin@portal.gov", role="admin")
    admin_user.set_password("admin123")
    session.add(admin_user)

    # College
    college_user = User(email="dean@university.edu", role="college")
    college_user.set_password("password123")
    session.add(college_user)
    session.flush()

    college = College(
        user_id=college_user.id,
        college_name="National Institute of Engineering & Technology",
        code="NIET-BLR",
        location="Bengaluru, Karnataka",
        contact_email="placements@niet.edu",
        website="https://niet.edu"
    )
    session.add(college)
    session.flush()

    # Companies
    company1_user = User(email="hr@techcorp.com", role="company")
    company1_user.set_password("password123")
    session.add(company1_user)
    session.flush()

    company1 = Company(
        user_id=company1_user.id,
        company_name="TechCorp Innovations Ltd.",
        industry_type="Cloud & Enterprise Software",
        website="https://techcorp.io",
        location="Bengaluru, Karnataka",
        description="Global digital engineering provider building cloud-native SaaS and AI platforms."
    )
    session.add(company1)

    company2_user = User(email="hr@datanexus.com", role="company")
    company2_user.set_password("password123")
    session.add(company2_user)
    session.flush()

    company2 = Company(
        user_id=company2_user.id,
        company_name="DataNexus AI Labs",
        industry_type="Artificial Intelligence & Analytics",
        website="https://datanexus.ai",
        location="Hyderabad, Telangana",
        description="Pioneering automated machine learning solutions for fintech and healthcare."
    )
    session.add(company2)
    session.flush()

    # Students
    stu1_user = User(email="student@demo.edu", role="student")
    stu1_user.set_password("password123")
    session.add(stu1_user)
    session.flush()

    stu1 = Student(
        user_id=stu1_user.id,
        college_id=college.id,
        full_name="Rahul Sharma",
        roll_no="22CS104",
        degree="B.Tech",
        branch="Computer Science & Engineering",
        graduation_year=2026,
        cgpa=8.7,
        bio="Passionate software engineering undergraduate interested in Backend Systems, Python, and Data Science.",
        target_career="Python Developer",
        location="Bengaluru, India",
        portfolio_slug="rahul-sharma"
    )
    session.add(stu1)
    session.flush()

    # Additional student profiles for college dashboard analytics
    stu2_user = User(email="ananya@demo.edu", role="student")
    stu2_user.set_password("password123")
    session.add(stu2_user)
    session.flush()

    stu2 = Student(
        user_id=stu2_user.id,
        college_id=college.id,
        full_name="Ananya Patel",
        roll_no="22IT045",
        degree="B.Tech",
        branch="Information Technology",
        graduation_year=2026,
        cgpa=9.1,
        bio="Full stack enthusiast specializing in React, Java, and modern microservices.",
        target_career="Full Stack Developer",
        location="Bengaluru, India",
        portfolio_slug="ananya-patel"
    )
    session.add(stu2)

    stu3_user = User(email="vikram@demo.edu", role="student")
    stu3_user.set_password("password123")
    session.add(stu3_user)
    session.flush()

    stu3 = Student(
        user_id=stu3_user.id,
        college_id=college.id,
        full_name="Vikram Reddy",
        roll_no="22CS089",
        degree="B.Tech",
        branch="Computer Science & Engineering",
        graduation_year=2026,
        cgpa=7.6,
        bio="Aspiring cloud engineer and system administrator.",
        target_career="Cloud DevOps Specialist",
        location="Hyderabad, India",
        portfolio_slug="vikram-reddy"
    )
    session.add(stu3)
    session.flush()

    # 4. Student Skills & Assessments for Rahul Sharma (stu1)
    rahul_skills = [
        ("Python", 85.0, 90.0, "Strong"),
        ("SQL", 80.0, 80.0, "Strong"),
        ("Git", 75.0, 75.0, "Strong"),
        ("Communication", 70.0, 75.0, "Strong"),
        ("Machine Learning", 45.0, 40.0, "Weak"),
        ("Cloud Computing", 30.0, 30.0, "Missing")
    ]
    for sk_name, prof, ver, stat in rahul_skills:
        session.add(StudentSkill(
            student_id=stu1.id,
            skill_id=skill_map[sk_name].id,
            proficiency_level=prof,
            verified_score=ver,
            status=stat
        ))

    # Ananya's skills
    ananya_skills = [
        ("Java", 85.0, 85.0, "Strong"),
        ("React", 90.0, 90.0, "Strong"),
        ("SQL", 75.0, 70.0, "Strong"),
        ("Communication", 80.0, 85.0, "Strong"),
        ("Cloud Computing", 35.0, 35.0, "Missing")
    ]
    for sk_name, prof, ver, stat in ananya_skills:
        session.add(StudentSkill(
            student_id=stu2.id,
            skill_id=skill_map[sk_name].id,
            proficiency_level=prof,
            verified_score=ver,
            status=stat
        ))

    # Vikram's skills
    vikram_skills = [
        ("Python", 65.0, 60.0, "Weak"),
        ("Cloud Computing", 75.0, 70.0, "Strong"),
        ("Git", 70.0, 70.0, "Strong"),
        ("Machine Learning", 30.0, 30.0, "Missing")
    ]
    for sk_name, prof, ver, stat in vikram_skills:
        session.add(StudentSkill(
            student_id=stu3.id,
            skill_id=skill_map[sk_name].id,
            proficiency_level=prof,
            verified_score=ver,
            status=stat
        ))

    # Rahul's Assessment Record
    assessment1 = SkillAssessment(
        student_id=stu1.id,
        technical_score=85.0,
        soft_skill_score=80.0,
        aptitude_score=85.0,
        overall_readiness=83.8,
        strong_skills_json=json.dumps(["Python", "SQL", "Git", "Communication"]),
        weak_skills_json=json.dumps(["Machine Learning"]),
        missing_skills_json=json.dumps(["Cloud Computing", "Cybersecurity"])
    )
    session.add(assessment1)

    # Ananya's Assessment Record
    assessment2 = SkillAssessment(
        student_id=stu2.id,
        technical_score=88.0,
        soft_skill_score=85.0,
        aptitude_score=90.0,
        overall_readiness=87.8,
        strong_skills_json=json.dumps(["Java", "React", "SQL", "Communication"]),
        weak_skills_json=json.dumps([]),
        missing_skills_json=json.dumps(["Cloud Computing", "Machine Learning"])
    )
    session.add(assessment2)

    # 5. Certificates & Projects for Rahul
    c1 = Certificate(
        student_id=stu1.id,
        title="Python for Data Science & AI",
        issuing_org="IBM Cognitive Class",
        issue_date="August 2025",
        credential_url="https://coursera.org/verify/sample-ibm-cert",
        status="Verified"
    )
    c2 = Certificate(
        student_id=stu1.id,
        title="PostgreSQL Relational Database Masterclass",
        issuing_org="Udemy / Meta Cert",
        issue_date="November 2025",
        credential_url="https://udemy.com/certificate/sample-sql",
        status="Verified"
    )
    session.add_all([c1, c2])

    p1 = Project(
        student_id=stu1.id,
        title="Smart Automated Attendance System",
        description="Built a real-time face recognition and attendance logging platform using Python OpenCV, SQLite, and Flask with 97% detection accuracy.",
        tech_stack="Python, OpenCV, Flask, SQLite",
        github_url="https://github.com/rahul-sharma/smart-attendance",
        live_url="https://smart-attendance-demo.onrender.com"
    )
    p2 = Project(
        student_id=stu1.id,
        title="Campus Event & Hackathon Portal",
        description="Full stack platform connecting collegiate clubs with sponsors and student participants, handling 1,500+ active event registrations.",
        tech_stack="Python, Flask, SQL, TailwindCSS",
        github_url="https://github.com/rahul-sharma/campus-events",
        live_url="https://campus-events-niet.vercel.app"
    )
    session.add_all([p1, p2])

    # 6. Jobs & Internships
    # Job 1
    job1 = Job(
        company_id=company1.id,
        title="Junior Python Developer",
        job_type="Full-time",
        description="We are looking for a sharp, driven Python Developer to develop high-throughput microservices, optimize database queries, and collaborate on automated CI/CD pipelines.",
        min_qualification="B.Tech / B.E in CSE, IT or related",
        experience_years=0,
        location="Bengaluru / Hybrid",
        salary="₹ 6,50,000 - ₹ 9,00,000 P.A.",
        status="Open"
    )
    session.add(job1)
    session.flush()

    for s_name, min_p, w in [("Python", 70.0, 1.2), ("SQL", 60.0, 1.0), ("Git", 60.0, 0.8)]:
        session.add(JobRequiredSkill(job_id=job1.id, skill_id=skill_map[s_name].id, min_proficiency=min_p, importance_weight=w))

    # Job 2
    job2 = Job(
        company_id=company2.id,
        title="Associate Machine Learning Engineer",
        job_type="Full-time",
        description="Design and train predictive models, fine-tune transformer pipelines, and deploy containerized ML endpoints into production.",
        min_qualification="B.Tech / M.Tech in CS/AI/Data Science",
        experience_years=0,
        location="Hyderabad / Remote",
        salary="₹ 8,00,000 - ₹ 12,00,000 P.A.",
        status="Open"
    )
    session.add(job2)
    session.flush()

    for s_name, min_p, w in [("Python", 75.0, 1.0), ("Machine Learning", 70.0, 1.3), ("SQL", 60.0, 0.9), ("Cloud Computing", 60.0, 0.8)]:
        session.add(JobRequiredSkill(job_id=job2.id, skill_id=skill_map[s_name].id, min_proficiency=min_p, importance_weight=w))

    # Job 3
    job3 = Job(
        company_id=company1.id,
        title="Full Stack Software Engineer",
        job_type="Full-time",
        description="Develop responsive client interfaces in React and robust RESTful API services in Python/Java.",
        min_qualification="B.Tech in Computer Science / IT",
        experience_years=0,
        location="Bengaluru",
        salary="₹ 7,00,000 - ₹ 11,00,000 P.A.",
        status="Open"
    )
    session.add(job3)
    session.flush()

    for s_name, min_p, w in [("React", 75.0, 1.1), ("Python", 70.0, 1.0), ("SQL", 65.0, 0.9)]:
        session.add(JobRequiredSkill(job_id=job3.id, skill_id=skill_map[s_name].id, min_proficiency=min_p, importance_weight=w))

    # Internship 1
    intern1 = Internship(
        company_id=company2.id,
        title="Data Analytics & AI Intern",
        internship_type="Summer Internship",
        description="3-month intensive hands-on internship focusing on exploratory data analysis, dashboarding, and feature engineering for enterprise banking clients.",
        duration_months=3,
        stipend="₹ 25,000 / month",
        location="Bengaluru / Hybrid",
        status="Open"
    )
    session.add(intern1)
    session.flush()

    for s_name, min_p, w in [("Python", 65.0, 1.0), ("SQL", 65.0, 1.0), ("Communication", 60.0, 0.8)]:
        session.add(JobRequiredSkill(internship_id=intern1.id, skill_id=skill_map[s_name].id, min_proficiency=min_p, importance_weight=w))

    # Internship 2
    intern2 = Internship(
        company_id=company1.id,
        title="Cloud Operations Intern",
        internship_type="Apprenticeship",
        description="Learn cloud infrastructure provisioning, container deployments, and monitoring with our senior DevOps engineering team.",
        duration_months=6,
        stipend="₹ 22,000 / month",
        location="Bengaluru",
        status="Open"
    )
    session.add(intern2)
    session.flush()

    for s_name, min_p, w in [("Cloud Computing", 65.0, 1.2), ("Git", 60.0, 0.9)]:
        session.add(JobRequiredSkill(internship_id=intern2.id, skill_id=skill_map[s_name].id, min_proficiency=min_p, importance_weight=w))

    # 7. Applications
    app1 = Application(
        student_id=stu1.id,
        job_id=job1.id,
        match_score=94.5,
        status="Shortlisted",
        cover_note="I have strong experience with Python backend development, SQLAlchemy, and automated testing."
    )
    app2 = Application(
        student_id=stu1.id,
        internship_id=intern1.id,
        match_score=82.0,
        status="Under Review",
        cover_note="Excited to apply analytical skills and SQL experience to enterprise projects."
    )
    app3 = Application(
        student_id=stu2.id,
        job_id=job3.id,
        match_score=92.0,
        status="Interview",
        cover_note="Full stack developer with rich experience in React and component design."
    )
    session.add_all([app1, app2, app3])

    # 8. Training Programs (Academia-Industry Collaboration)
    t1 = TrainingProgram(
        company_id=company2.id,
        title="Applied Machine Learning & MLOps Masterclass",
        program_type="Workshop",
        description="4-weekend hands-on workshop guiding students and faculty through real-world model deployment, data pipelines, and monitoring.",
        duration="4 Weeks (Weekends)",
        eligibility="Open to 3rd & 4th year B.Tech students and College Faculty",
        registration_link="https://datanexus.ai/workshops/mlops-2026"
    )
    t2 = TrainingProgram(
        company_id=company1.id,
        title="Cloud Computing & DevOps Faculty Development Program (FDP)",
        program_type="FDP",
        description="Intensive FDP designed to equip academic faculties with modern cloud deployment methodologies, containerization, and AWS architecture.",
        duration="2 Weeks",
        eligibility="Engineering Faculty & Academic Coordinators",
        registration_link="https://techcorp.io/fdp/cloud-2026"
    )
    t3 = TrainingProgram(
        company_id=company1.id,
        title="National Smart City Innovation Challenge",
        program_type="Live Project",
        description="Collaborative live industrial challenge solving civic data management problems with direct corporate mentorship and incubation funding.",
        duration="6 Weeks",
        eligibility="Cross-functional student teams (up to 4 members)",
        registration_link="https://techcorp.io/challenge/smart-city"
    )
    session.add_all([t1, t2, t3])

    # 9. Mentorship Program
    m1 = MentorshipProgram(
        company_id=company1.id,
        mentor_name="Dr. Arvind Narayanan",
        domain="Distributed Systems & Cloud Architecture",
        description="Bi-weekly 1-on-1 career guidance sessions for pre-final year students.",
        sessions_count=6,
        contact_email="arvind.n@techcorp.io"
    )
    session.add(m1)

    # 10. Notifications
    notifs = [
        Notification(user_id=stu1_user.id, title="New High-Match Job Found!", message="TechCorp Innovations posted 'Junior Python Developer' matching 94.5% of your skill profile.", category="JobMatch"),
        Notification(user_id=stu1_user.id, title="Application Shortlisted", message="Congratulations! TechCorp Innovations has shortlisted your application for 'Junior Python Developer'.", category="Application"),
        Notification(user_id=stu1_user.id, title="Skill Gap Recommendation", message="Closing your skill gap in 'Cloud Computing' can boost your job match rates by 35%.", category="Assessment"),
        Notification(user_id=company1_user.id, title="New Qualified Applicant", message="Rahul Sharma (94.5% Match) applied for 'Junior Python Developer'.", category="Application")
    ]
    session.add_all(notifs)

    session.commit()
    session.close()
    print("Database successfully seeded with realistic demo data.")

if __name__ == "__main__":
    seed_database()
