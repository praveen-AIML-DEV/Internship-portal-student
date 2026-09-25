# Smart Academia–Industry Collaboration Portal for Skill Mapping, Internships and Placement

**Theme:** Smart Automation  
**Platform Name:** EduConnect AI &bull; Smart Academia–Industry Synergy  
**Stack:** Python (Flask), SQLAlchemy, SQLite / MySQL, JavaScript, HTML5, Tailwind CSS, Chart.js

---

## 📌 Problem Statement & Overview
There is a persistent gap between academic curricula in higher educational institutions and real-world skills demanded by industry. Students lack visibility into what skills companies look for; recruiters spend excessive manual effort screening resumes with opaque match criteria; and colleges lack real-time visibility into current industry demand to adjust curricula.

This project delivers a **Smart Academia–Industry Collaboration Portal** that connects **Students**, **Companies**, **Colleges**, and **Administrators** on an automated, transparent platform.

---

## 🚀 Key Smart Automation Features
1. **Automated AI Skill Assessment**: Adaptive evaluation across Technical, Soft Skills, and Aptitude domains.
2. **Instant Skill-Gap Detection**: Highlights Strong competencies ($\ge 70\%$) and classifies Missing Skill Gaps ($< 40\%$).
3. **Transparent Hybrid Matching Engine**: Ranks jobs and internships with explainable match percentages, showing matched skills vs missing skills.
4. **Interactive Career Recommendations**: Guides students on target learning pathways to unlock higher match rates.
5. **Real-time Application Pipeline**: Tracks progress through `Applied` $\to$ `Under Review` $\to$ `Shortlisted` $\to$ `Interview` $\to$ `Selected`/`Rejected`.
6. **Institutional Analytics & Demand Barometer**: Real-time Chart.js dashboards showing college student skill distributions and top missing curriculum skills.
7. **Public Verifiable Digital Portfolio**: Shareable portfolios (`/portfolio/<slug>`) with verified AI score badges and project repositories.
8. **Industry Learning & Collaboration Hub**: Enables corporate partners to post Faculty Development Programs (FDPs), bootcamps, and live industrial challenges.

---

## 👥 Member-Wise Development Modules

| Module | Team Member | Primary Tech | Responsibility & Key Deliverables |
|---|---|---|---|
| **Member 1** | AI Skill Assessment | Python + Google Colab | Assessment engine, question bank, multi-tier scoring (Tech, Soft, Aptitude), readiness index, and standalone Colab notebook (`colab_assessment_demo.ipynb`). |
| **Member 2** | Student Website | HTML, JS, Tailwind, CSS | Student portal, interactive test runner, skill radar breakdown, recommended opportunities, application tracker, and public portfolio. |
| **Member 3** | Company Website | HTML, JS, UI | Employer portal, job/internship posting with skill tags, candidate applicant ranking by match %, shortlisting pipeline, and industry collaborations. |
| **Member 4** | AI Job Matching Engine | Python Engine | Multi-factor transparent scoring engine (Skill overlap 50%, Proficiency 25%, Qualification 15%, Location/Interests 10%) with explainable rationale (`matching_engine.py`). |
| **Member 5** | College Dashboard | HTML, Chart.js, JS | Institutional analytics dashboard: student skill proficiencies, placement readiness index, top missing curriculum skills, and industry demand barometer. |
| **Member 6** | Database & Integration | Flask REST API + MySQL / SQLite | Unified RESTful backend, SQLAlchemy ORM with 19 normalized tables, dual database support, authentication, role control, and seed data. |

---

## 🏛️ System Architecture

```
                    ┌────────────────────────────────────────────────────────┐
                    │                      FRONTEND                          │
                    │   Student Portal  |  Company Portal  | College Portal  │
                    │   Admin Portal    |  Public Shareable Portfolio        │
                    └───────────────────────────┬────────────────────────────┘
                                                │ REST API / JSON
                                                ▼
                    ┌────────────────────────────────────────────────────────┐
                    │                 FLASK BACKEND (Member 6)               │
                    │  Authentication | Role Control | REST Endpoints        │
                    └─────┬─────────────────────┬──────────────────────┬─────┘
                          │                     │                      │
                          ▼                     ▼                      ▼
               ┌─────────────────────┐┌───────────────────┐┌────────────────────┐
               │ AI Skill Assessment ││ AI Matching Engine││ College Analytics  │
               │     (Member 1)      ││    (Member 4)     ││     (Member 5)     │
               └──────────┬──────────┘└─────────┬─────────┘└──────────┬─────────┘
                          │                     │                     │
                          └─────────────────────┼─────────────────────┘
                                                ▼
                    ┌────────────────────────────────────────────────────────┐
                    │               DATABASE LAYER (Member 6)                │
                    │   SQLite (Zero-setup default) / MySQL (schema.sql)     │
                    │   19 Normalized Tables + Comprehensive Seed Data       │
                    └────────────────────────────────────────────────────────┘
```

---

## ⚡ Quick Start & Execution

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Seed Database (Optional - Pre-seeded out of the box)
```bash
python seed_data.py
```

### 3. Launch Web Portal
```bash
python app.py
```
Open your browser at: **`http://127.0.0.1:5000`**

---

## 🔑 Pre-Seeded Demo Credentials

A quick **Role Switcher Demo Bar** is available at the top of every page, allowing instant 1-click switching between accounts without re-entering credentials!

| Role | Email | Password | Pre-populated Data |
|---|---|---|---|
| **Student** | `student@demo.edu` | `password123` | Rahul Sharma (B.Tech CSE, 8.7 CGPA, AI Score: 83.8%, Python/SQL/Git, Shortlisted app) |
| **Company** | `hr@techcorp.com` | `password123` | TechCorp Innovations (Active jobs, candidate applicants with match scores) |
| **College** | `dean@university.edu` | `password123` | National Institute of Engineering & Technology (Analytics charts, student roster) |
| **Admin** | `admin@portal.gov` | `admin123` | Portal Governance & Verification Dashboard |

---

## 🧪 Running Automated Unit Tests

- **Assessment & AI Matching Tests**:
  ```bash
  python -m unittest tests/test_assessment.py
  ```
- **Member 4 Standalone Matching CLI Demo**:
  ```bash
  python modules/matching_engine/test_matching_standalone.py
  ```
- **Complete Flask REST API Integration Tests**:
  ```bash
  python -m unittest tests/test_api.py
  ```

---

## 📁 Repository Directory Structure

```
smart_academia_industry_portal/
├── app.py                               # Central Flask application entrypoint & routing
├── config.py                            # Environment & database configuration
├── models.py                            # SQLAlchemy ORM definitions (19 normalized tables)
├── schema.sql                           # MySQL DDL schema export for Member 6
├── seed_data.py                         # Database initialization & realistic demonstration data
├── requirements.txt                     # Python dependencies
├── modules/
│   ├── ai_assessment/
│   │   ├── assessment_engine.py         # Member 1: AI Assessment & Skill Gap Engine
│   │   ├── question_bank.json           # Categorized questions (Tech, Soft, Aptitude)
│   │   └── colab_assessment_demo.ipynb  # Member 1: Standalone Google Colab / Jupyter Notebook
│   └── matching_engine/
│       ├── matching_engine.py           # Member 4: AI Transparent Job Matching Engine
│       └── test_matching_standalone.py  # Member 4: Standalone test script & demonstration
├── routes/
│   ├── auth_routes.py                   # Role-based login, register, role switcher
│   ├── student_routes.py                # Member 2: Student pages & REST APIs
│   ├── company_routes.py                # Member 3: Company pages & REST APIs
│   ├── college_routes.py                # Member 5: College analytics & student roster
│   ├── admin_routes.py                  # Admin verification & governance
│   └── api_routes.py                    # Notifications & common REST endpoints
├── static/
│   ├── css/style.css                    # Custom styles, badges, and animations
│   └── js/app.js                        # Toast alerts, notification popover
├── templates/
│   ├── base.html                        # Base layout, navbar, top demo switcher, footer
│   ├── index.html                       # Smart India Hackathon Landing Page
│   ├── login.html                       # Dual-tab login & registration
│   ├── student/                         # Member 2 Templates
│   │   ├── dashboard.html
│   │   ├── profile.html
│   │   ├── assessment.html
│   │   ├── jobs.html
│   │   ├── applications.html
│   │   └── portfolio.html
│   ├── company/                         # Member 3 Templates
│   │   ├── dashboard.html
│   │   ├── post_job.html
│   │   ├── applicants.html
│   │   ├── collaborations.html
│   │   └── profile.html
│   ├── college/                         # Member 5 Templates
│   │   ├── dashboard.html
│   │   ├── students.html
│   │   └── collaboration.html
│   └── admin/
│       └── dashboard.html               # Admin Governance Dashboard
└── tests/
    ├── test_assessment.py               # Unit tests for AI Assessment & Matching
    └── test_api.py                      # Integration tests for Flask endpoints
```
