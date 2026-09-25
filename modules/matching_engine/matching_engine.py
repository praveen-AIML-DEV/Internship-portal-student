from typing import Dict, List, Any, Optional

class AIJobMatchingEngine:
    """
    Member 4: Intelligent Job & Internship Matching Engine.
    Provides transparent, multi-factor scoring:
    - Skill Overlap (50%)
    - Skill Proficiency (25%)
    - Qualification & Branch Eligibility (15%)
    - Career Interest & Location Alignment (10%)
    """

    def __init__(self, weight_overlap=0.50, weight_prof=0.25, weight_qual=0.15, weight_pref=0.10):
        self.w_overlap = weight_overlap
        self.w_prof = weight_prof
        self.w_qual = weight_qual
        self.w_pref = weight_pref

    def calculate_match(self, student_profile: Dict[str, Any], opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates match score between student profile and job/internship opportunity.
        
        student_profile: {
            'skills': {'Python': 85.0, 'SQL': 75.0, ...}, # skill name -> proficiency
            'degree': 'B.Tech',
            'branch': 'Computer Science',
            'cgpa': 8.5,
            'target_career': 'Data Analyst',
            'location': 'Bengaluru'
        }
        
        opportunity: {
            'id': 1,
            'title': 'Junior Python Developer',
            'type': 'Job', # or 'Internship'
            'required_skills': [
                {'name': 'Python', 'min_proficiency': 70.0, 'weight': 1.0},
                {'name': 'SQL', 'min_proficiency': 60.0, 'weight': 1.0},
                {'name': 'Machine Learning', 'min_proficiency': 50.0, 'weight': 1.0}
            ],
            'min_qualification': 'B.Tech',
            'preferred_branches': ['Computer Science', 'Information Technology'],
            'location': 'Bengaluru / Hybrid'
        }
        """
        student_skills = {k.strip().lower(): v for k, v in student_profile.get('skills', {}).items()}
        req_skills_raw = opportunity.get('required_skills', [])

        # Normalize required skills
        req_skills = []
        for r in req_skills_raw:
            if isinstance(r, str):
                req_skills.append({'name': r.strip(), 'min_proficiency': 50.0, 'weight': 1.0})
            elif isinstance(r, dict):
                req_skills.append({
                    'name': r.get('name', '').strip(),
                    'min_proficiency': float(r.get('min_proficiency', 50.0)),
                    'weight': float(r.get('weight', 1.0))
                })

        total_req = len(req_skills)
        matched_skills = []
        missing_skills = []
        prof_ratios = []

        if total_req > 0:
            for req in req_skills:
                s_name = req['name']
                s_lower = s_name.lower()
                min_p = req['min_proficiency']

                if s_lower in student_skills:
                    stu_score = float(student_skills[s_lower])
                    matched_skills.append({
                        'name': s_name,
                        'student_score': stu_score,
                        'required_min': min_p
                    })
                    # Proficiency factor
                    ratio = min(1.0, stu_score / max(1.0, min_p))
                    prof_ratios.append(ratio)
                else:
                    missing_skills.append({
                        'name': s_name,
                        'required_min': min_p
                    })

            overlap_score = (len(matched_skills) / total_req) * 100.0
            prof_score = (sum(prof_ratios) / total_req) * 100.0 if prof_ratios else 0.0
        else:
            overlap_score = 100.0
            prof_score = 100.0

        # Academic / Qualification Factor
        qual_score = self._calc_qualification_match(student_profile, opportunity)

        # Career Interest & Location Alignment
        pref_score = self._calc_preference_match(student_profile, opportunity)

        # Final Weighted Score
        total_score = (
            (self.w_overlap * overlap_score) +
            (self.w_prof * prof_score) +
            (self.w_qual * qual_score) +
            (self.w_pref * pref_score)
        )
        total_score = round(min(100.0, max(0.0, total_score)), 1)

        # Transparent explanation generator
        explanation = self._build_explanation(
            total_score=total_score,
            total_req=total_req,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            qual_score=qual_score,
            opp_title=opportunity.get('title', 'Role')
        )

        return {
            'opportunity_id': opportunity.get('id'),
            'opportunity_title': opportunity.get('title'),
            'opportunity_type': opportunity.get('type', 'Job'),
            'match_percentage': total_score,
            'skill_overlap_score': round(overlap_score, 1),
            'proficiency_score': round(prof_score, 1),
            'matched_skills': [m['name'] for m in matched_skills],
            'missing_skills': [m['name'] for m in missing_skills],
            'matched_details': matched_skills,
            'missing_details': missing_skills,
            'explanation': explanation
        }

    def _calc_qualification_match(self, student: Dict[str, Any], opportunity: Dict[str, Any]) -> float:
        score = 80.0
        deg = student.get('degree', '').lower()
        branch = student.get('branch', '').lower()
        min_q = str(opportunity.get('min_qualification', '')).lower()

        if min_q and any(k in deg for k in ['b.tech', 'b.e', 'mca', 'm.tech', 'bca', 'b.sc']):
            score += 10.0

        pref_branches = [b.lower() for b in opportunity.get('preferred_branches', [])]
        if pref_branches:
            if any(b in branch for b in pref_branches):
                score += 10.0
        else:
            score += 10.0

        cgpa = float(student.get('cgpa', 7.5))
        if cgpa >= 8.0:
            score += 5.0

        return min(100.0, score)

    def _calc_preference_match(self, student: Dict[str, Any], opportunity: Dict[str, Any]) -> float:
        score = 70.0
        target_career = student.get('target_career', '').lower()
        title = opportunity.get('title', '').lower()

        # Domain overlap
        words = [w for w in target_career.split() if len(w) > 3]
        if any(w in title for w in words):
            score += 20.0

        # Location matching
        stu_loc = student.get('location', '').lower()
        opp_loc = opportunity.get('location', '').lower()
        if 'remote' in opp_loc or 'hybrid' in opp_loc or any(c in opp_loc for c in stu_loc.split(',')):
            score += 10.0

        return min(100.0, score)

    def _build_explanation(self, total_score: float, total_req: int, matched_skills: List[Dict],
                           missing_skills: List[Dict], qual_score: float, opp_title: str) -> str:
        matched_names = ", ".join([m['name'] for m in matched_skills]) or "None"
        missing_names = ", ".join([m['name'] for m in missing_skills]) or "None"
        reasons = []

        if matched_skills:
            reasons.append(f"Matched {len(matched_skills)}/{total_req} core skills: {matched_names}")
        if missing_skills:
            reasons.append(f"Skill gap identified: Learn {missing_names} to maximize hiring potential")
        if qual_score >= 85:
            reasons.append("Academic degree & discipline strongly match eligibility requirements")

        return f"{opp_title} ({total_score}% Fit): " + "; ".join(reasons) + "."

    def rank_opportunities(self, student_profile: Dict[str, Any],
                           opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ranks all jobs and internships for a student by match percentage."""
        scored = [self.calculate_match(student_profile, opp) for opp in opportunities]
        scored.sort(key=lambda x: x['match_percentage'], reverse=True)
        return scored
