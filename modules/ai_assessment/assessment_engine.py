import json
import os
from typing import Dict, List, Any, Tuple

class AIAssessmentEngine:
    """
    Member 1: AI Skill Assessment Engine
    Evaluates student assessments, computes domain & granular skill scores,
    classifies strong/weak/missing skills, and produces a structured profile.
    """

    def __init__(self, question_bank_path: str = None):
        if question_bank_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            question_bank_path = os.path.join(base_dir, 'question_bank.json')
        self.question_bank_path = question_bank_path
        self.questions = self._load_questions()

    def _load_questions(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.question_bank_path):
            with open(self.question_bank_path, 'r', encoding='utf-8-sig') as f:
                return json.load(f)
        return []

    def evaluate_answers(self, submissions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate student's submitted answers.
        
        Input:
            submissions: list of dicts with:
                - question_id or question_text or question index
                - category: 'Technical' | 'Soft Skills' | 'Aptitude'
                - skill: e.g. 'Python', 'SQL', 'Communication'
                - selected_option: 'A' | 'B' | 'C' | 'D'
                - correct_option: 'A' | 'B' | 'C' | 'D'
        
        Returns:
            Structured profile with category scores, skill-wise breakdown,
            strong/weak/missing categorizations, and overall readiness index.
        """
        category_stats = {
            'Technical': {'correct': 0, 'total': 0},
            'Soft Skills': {'correct': 0, 'total': 0},
            'Aptitude': {'correct': 0, 'total': 0}
        }
        skill_stats: Dict[str, Dict[str, int]] = {}

        evaluated_answers = []

        for sub in submissions:
            category = sub.get('category', 'Technical')
            skill = sub.get('skill', 'General')
            selected = sub.get('selected_option', '').strip().upper()
            correct = sub.get('correct_option', '').strip().upper()
            is_correct = (selected == correct and bool(selected))

            if category not in category_stats:
                category_stats[category] = {'correct': 0, 'total': 0}
            category_stats[category]['total'] += 1
            if is_correct:
                category_stats[category]['correct'] += 1

            if skill not in skill_stats:
                skill_stats[skill] = {'correct': 0, 'total': 0, 'category': category}
            skill_stats[skill]['total'] += 1
            if is_correct:
                skill_stats[skill]['correct'] += 1

            evaluated_answers.append({
                'question_id': sub.get('question_id'),
                'skill': skill,
                'category': category,
                'selected_option': selected,
                'correct_option': correct,
                'is_correct': is_correct
            })

        # Calculate category percentages
        tech_score = self._calc_percentage(category_stats['Technical']['correct'], category_stats['Technical']['total'])
        soft_score = self._calc_percentage(category_stats['Soft Skills']['correct'], category_stats['Soft Skills']['total'])
        apt_score = self._calc_percentage(category_stats['Aptitude']['correct'], category_stats['Aptitude']['total'])

        # Weighted Overall Readiness Index (50% Tech, 25% Soft, 25% Aptitude)
        overall_readiness = round((tech_score * 0.50) + (soft_score * 0.25) + (apt_score * 0.25), 1)

        # Granular Skill-wise breakdown
        skill_breakdown = {}
        strong_skills = []
        weak_skills = []
        missing_skills = []

        for skill_name, data in skill_stats.items():
            pct = self._calc_percentage(data['correct'], data['total'])
            skill_breakdown[skill_name] = {
                'score': pct,
                'category': data['category'],
                'attempted': data['total'],
                'correct': data['correct']
            }

            if pct >= 70.0:
                strong_skills.append(skill_name)
            elif pct >= 40.0:
                weak_skills.append(skill_name)
            else:
                missing_skills.append(skill_name)

        return {
            'technical_score': tech_score,
            'soft_skill_score': soft_score,
            'aptitude_score': apt_score,
            'overall_readiness': overall_readiness,
            'skill_breakdown': skill_breakdown,
            'strong_skills': strong_skills,
            'weak_skills': weak_skills,
            'missing_skills': missing_skills,
            'evaluated_answers': evaluated_answers
        }

    @staticmethod
    def _calc_percentage(correct: int, total: int) -> float:
        if total == 0:
            return 0.0
        return round((correct / total) * 100.0, 1)

    def generate_recommendations(self, missing_skills: List[str], strong_skills: List[str]) -> List[str]:
        """Suggest actionable learning steps based on identified gaps."""
        recs = []
        for s in missing_skills:
            recs.append(f"Accelerate fundamental hands-on training in '{s}'.")
        for s in strong_skills:
            recs.append(f"Leverage your strength in '{s}' for advanced domain projects and technical interviews.")
        return recs


if __name__ == '__main__':
    engine = AIAssessmentEngine()
    print(f"Loaded {len(engine.questions)} questions from question bank.")
    sample_subs = [
        {'skill': 'Python', 'category': 'Technical', 'selected_option': 'B', 'correct_option': 'B'},
        {'skill': 'Python', 'category': 'Technical', 'selected_option': 'B', 'correct_option': 'B'},
        {'skill': 'SQL', 'category': 'Technical', 'selected_option': 'C', 'correct_option': 'C'},
        {'skill': 'Machine Learning', 'category': 'Technical', 'selected_option': 'A', 'correct_option': 'B'},
        {'skill': 'Communication', 'category': 'Soft Skills', 'selected_option': 'B', 'correct_option': 'B'},
        {'skill': 'Quantitative Aptitude', 'category': 'Aptitude', 'selected_option': 'B', 'correct_option': 'B'}
    ]
    res = engine.evaluate_answers(sample_subs)
    print("AI Evaluation Result:")
    print(json.dumps(res, indent=2))
