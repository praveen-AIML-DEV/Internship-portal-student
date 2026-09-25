import json
from matching_engine import AIJobMatchingEngine

def run_demo():
    print("================================================================")
    print(" MEMBER 4: AI JOB MATCHING ENGINE DEMONSTRATION")
    print("================================================================\n")

    engine = AIJobMatchingEngine()

    # Sample Student Profile
    student = {
        'skills': {
            'Python': 85.0,
            'SQL': 80.0,
            'Git': 75.0,
            'Communication': 70.0
        },
        'degree': 'B.Tech',
        'branch': 'Computer Science & Engineering',
        'cgpa': 8.6,
        'target_career': 'Python Developer',
        'location': 'Bengaluru'
    }

    # Sample Industry Opportunities
    opportunities = [
        {
            'id': 101,
            'title': 'Junior Python Developer',
            'type': 'Job',
            'required_skills': [
                {'name': 'Python', 'min_proficiency': 70.0},
                {'name': 'SQL', 'min_proficiency': 60.0},
                {'name': 'Git', 'min_proficiency': 60.0}
            ],
            'min_qualification': 'B.Tech',
            'preferred_branches': ['Computer Science', 'IT'],
            'location': 'Bengaluru'
        },
        {
            'id': 102,
            'title': 'Data Analyst Intern',
            'type': 'Internship',
            'required_skills': [
                {'name': 'Python', 'min_proficiency': 60.0},
                {'name': 'SQL', 'min_proficiency': 70.0},
                {'name': 'Data Visualization', 'min_proficiency': 60.0}
            ],
            'min_qualification': 'B.Tech',
            'preferred_branches': ['Computer Science', 'Data Science'],
            'location': 'Bengaluru / Hybrid'
        },
        {
            'id': 103,
            'title': 'Machine Learning Engineer',
            'type': 'Job',
            'required_skills': [
                {'name': 'Python', 'min_proficiency': 80.0},
                {'name': 'Machine Learning', 'min_proficiency': 75.0},
                {'name': 'Deep Learning', 'min_proficiency': 70.0},
                {'name': 'Cloud Computing', 'min_proficiency': 65.0}
            ],
            'min_qualification': 'B.Tech / M.Tech',
            'preferred_branches': ['Computer Science', 'AI'],
            'location': 'Bengaluru'
        },
        {
            'id': 104,
            'title': 'Cloud DevOps Specialist',
            'type': 'Job',
            'required_skills': [
                {'name': 'Cloud Computing', 'min_proficiency': 75.0},
                {'name': 'Docker', 'min_proficiency': 70.0},
                {'name': 'Kubernetes', 'min_proficiency': 65.0},
                {'name': 'Linux', 'min_proficiency': 70.0}
            ],
            'min_qualification': 'B.Tech',
            'preferred_branches': ['Computer Science', 'IT'],
            'location': 'Bengaluru'
        }
    ]

    print("Student Skills Profile:")
    for s, p in student['skills'].items():
        print(f"  - {s}: {p}%")
    print(f"Target Career: {student['target_career']}\n")

    ranked = engine.rank_opportunities(student, opportunities)

    print("--- RANKED OPPORTUNITIES (By Transparent AI Match Score) ---\n")
    for idx, opp in enumerate(ranked, 1):
        print(f"Rank {idx}: {opp['opportunity_title']} ({opp['opportunity_type']})")
        print(f"  Match Score: {opp['match_percentage']}%")
        print(f"  Skill Overlap: {opp['skill_overlap_score']}% | Proficiency Factor: {opp['proficiency_score']}%")
        print(f"  Matched Skills: {', '.join(opp['matched_skills']) if opp['matched_skills'] else 'None'}")
        print(f"  Missing Skills: {', '.join(opp['missing_skills']) if opp['missing_skills'] else 'None'}")
        print(f"  Transparent Rationale: {opp['explanation']}")
        print()

if __name__ == '__main__':
    run_demo()
