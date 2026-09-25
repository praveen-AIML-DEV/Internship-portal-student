-- ==============================================================================
-- Smart Academia-Industry Collaboration Portal
-- MySQL DDL Schema Definition (Member 6)
-- ==============================================================================

DROP DATABASE IF EXISTS academia_portal;
CREATE DATABASE academia_portal CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE academia_portal;

-- 1. Users Table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    role VARCHAR(30) NOT NULL, -- 'student', 'company', 'college', 'admin'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_user_email (email)
) ENGINE=InnoDB;

-- 2. Colleges Table
CREATE TABLE colleges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    college_name VARCHAR(200) NOT NULL,
    code VARCHAR(50),
    location VARCHAR(120),
    contact_email VARCHAR(120),
    website VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 3. Students Table
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    college_id INT NULL,
    full_name VARCHAR(120) NOT NULL,
    roll_no VARCHAR(50),
    degree VARCHAR(100) DEFAULT 'B.Tech',
    branch VARCHAR(100) DEFAULT 'Computer Science',
    graduation_year INT DEFAULT 2026,
    cgpa FLOAT DEFAULT 8.0,
    bio TEXT,
    target_career VARCHAR(120) DEFAULT 'Software Engineer',
    location VARCHAR(100) DEFAULT 'Bengaluru, India',
    portfolio_slug VARCHAR(100) NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (college_id) REFERENCES colleges(id) ON DELETE SET NULL,
    INDEX idx_student_slug (portfolio_slug)
) ENGINE=InnoDB;

-- 4. Companies Table
CREATE TABLE companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    company_name VARCHAR(150) NOT NULL,
    industry_type VARCHAR(100) DEFAULT 'Information Technology',
    website VARCHAR(255),
    location VARCHAR(120) DEFAULT 'Bengaluru, India',
    description TEXT,
    verified BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 5. Skills Table
CREATE TABLE skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50) DEFAULT 'Technical',
    description TEXT,
    INDEX idx_skill_name (name)
) ENGINE=InnoDB;

-- 6. Student Skills Table
CREATE TABLE student_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    skill_id INT NOT NULL,
    proficiency_level FLOAT DEFAULT 50.0,
    verified_score FLOAT DEFAULT 0.0,
    status VARCHAR(30) DEFAULT 'Weak',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    UNIQUE KEY uq_student_skill (student_id, skill_id)
) ENGINE=InnoDB;

-- 7. Skill Assessments Table
CREATE TABLE skill_assessments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    technical_score FLOAT DEFAULT 0.0,
    soft_skill_score FLOAT DEFAULT 0.0,
    aptitude_score FLOAT DEFAULT 0.0,
    overall_readiness FLOAT DEFAULT 0.0,
    strong_skills_json TEXT,
    weak_skills_json TEXT,
    missing_skills_json TEXT,
    completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 8. Assessment Questions Table
CREATE TABLE assessment_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    skill_id INT NULL,
    category VARCHAR(50) DEFAULT 'Technical',
    question_text TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_option VARCHAR(5) NOT NULL,
    difficulty VARCHAR(20) DEFAULT 'Intermediate',
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 9. Assessment Answers Table
CREATE TABLE assessment_answers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    assessment_id INT NOT NULL,
    question_id INT NOT NULL,
    selected_option VARCHAR(5) NOT NULL,
    is_correct BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (assessment_id) REFERENCES skill_assessments(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES assessment_questions(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 10. Certificates Table
CREATE TABLE certificates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    issuing_org VARCHAR(150) NOT NULL,
    issue_date VARCHAR(50),
    credential_url VARCHAR(255),
    status VARCHAR(30) DEFAULT 'Verified',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 11. Projects Table
CREATE TABLE projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    tech_stack VARCHAR(255),
    github_url VARCHAR(255),
    live_url VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 12. Jobs Table
CREATE TABLE jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    job_type VARCHAR(50) DEFAULT 'Full-time',
    description TEXT NOT NULL,
    min_qualification VARCHAR(100) DEFAULT 'B.Tech / B.E / BCA',
    experience_years INT DEFAULT 0,
    location VARCHAR(120) DEFAULT 'Bengaluru / Hybrid',
    salary VARCHAR(100) DEFAULT '₹ 6,00,000 - ₹ 10,00,000 P.A.',
    status VARCHAR(30) DEFAULT 'Open',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 13. Internships Table
CREATE TABLE internships (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    internship_type VARCHAR(50) DEFAULT 'Summer Internship',
    description TEXT NOT NULL,
    duration_months INT DEFAULT 3,
    stipend VARCHAR(100) DEFAULT '₹ 25,000 / month',
    location VARCHAR(120) DEFAULT 'Remote / Bengaluru',
    status VARCHAR(30) DEFAULT 'Open',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 14. Job Required Skills Table
CREATE TABLE job_required_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NULL,
    internship_id INT NULL,
    skill_id INT NOT NULL,
    importance_weight FLOAT DEFAULT 1.0,
    min_proficiency FLOAT DEFAULT 60.0,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    FOREIGN KEY (internship_id) REFERENCES internships(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 15. Applications Table
CREATE TABLE applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    job_id INT NULL,
    internship_id INT NULL,
    match_score FLOAT DEFAULT 0.0,
    status VARCHAR(30) DEFAULT 'Applied', -- 'Applied', 'Under Review', 'Shortlisted', 'Interview', 'Selected', 'Rejected'
    cover_note TEXT,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    FOREIGN KEY (internship_id) REFERENCES internships(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 16. Skill Matches Table
CREATE TABLE skill_matches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    job_id INT NULL,
    internship_id INT NULL,
    match_percentage FLOAT DEFAULT 0.0,
    matched_skills_json TEXT,
    missing_skills_json TEXT,
    explanation TEXT,
    calculated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    FOREIGN KEY (internship_id) REFERENCES internships(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 17. Training Programs Table
CREATE TABLE training_programs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NULL,
    college_id INT NULL,
    title VARCHAR(200) NOT NULL,
    program_type VARCHAR(50) DEFAULT 'Workshop', -- 'Training', 'Certification', 'Workshop', 'FDP', 'Live Project'
    description TEXT NOT NULL,
    duration VARCHAR(100) DEFAULT '4 Weeks',
    eligibility VARCHAR(200) DEFAULT 'Open to all pre-final & final year students',
    registration_link VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    FOREIGN KEY (college_id) REFERENCES colleges(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 18. Mentorship Programs Table
CREATE TABLE mentorship_programs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    mentor_name VARCHAR(120) NOT NULL,
    domain VARCHAR(120) DEFAULT 'AI / Data Science',
    description TEXT,
    sessions_count INT DEFAULT 6,
    contact_email VARCHAR(120),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 19. Notifications Table
CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    category VARCHAR(50) DEFAULT 'System',
    is_read BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;
