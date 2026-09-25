import unittest
import sys
import os

# Include app path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules.ai_assessment.assessment_engine import AIAssessmentEngine
from modules.matching_engine.matching_engine import AIJobMatchingEngine

class TestAIAssessmentEngine(unittest.TestCase):
    def setUp(self):
        self.engine = AIAssessmentEngine()

    def test_evaluation_calculation(self):
        sample_submissions = [
            {'category': 'Technical', 'skill': 'Python', 'selected_option': 'B', 'correct_option': 'B'},
            {'category': 'Technical', 'skill': 'Python', 'selected_option': 'B', 'correct_option': 'B'},
            {'category': 'Technical', 'skill': 'SQL', 'selected_option': 'C', 'correct_option': 'C'},
            {'category': 'Technical', 'skill': 'Machine Learning', 'selected_option': 'A', 'correct_option': 'B'},
            {'category': 'Soft Skills', 'skill': 'Communication', 'selected_option': 'B', 'correct_option': 'B'},
            {'category': 'Aptitude', 'skill': 'Quantitative Aptitude', 'selected_option': 'B', 'correct_option': 'B'}
        ]
        result = self.engine.evaluate_answers(sample_submissions)

        # Technical: 3 correct out of 4 = 75.0%
        self.assertEqual(result['technical_score'], 75.0)
        # Soft: 1/1 = 100.0%
        self.assertEqual(result['soft_skill_score'], 100.0)
        # Aptitude: 1/1 = 100.0%
        self.assertEqual(result['aptitude_score'], 100.0)

        # Readiness = (75 * 0.5) + (100 * 0.25) + (100 * 0.25) = 37.5 + 25 + 25 = 87.5%
        self.assertEqual(result['overall_readiness'], 87.5)

        # Check strong and missing skills
        self.assertIn('Python', result['strong_skills'])
        self.assertIn('SQL', result['strong_skills'])
        self.assertIn('Machine Learning', result['missing_skills'])

class TestMatchingEngine(unittest.TestCase):
    def setUp(self):
        self.matching = AIJobMatchingEngine()

    def test_skill_match_calculation(self):
        student = {
            'skills': {'Python': 90.0, 'SQL': 80.0},
            'degree': 'B.Tech',
            'branch': 'Computer Science',
            'cgpa': 8.5,
            'target_career': 'Python Developer',
            'location': 'Bengaluru'
        }
        opp = {
            'id': 1,
            'title': 'Junior Python Developer',
            'type': 'Job',
            'required_skills': ['Python', 'SQL'],
            'min_qualification': 'B.Tech',
            'location': 'Bengaluru'
        }
        res = self.matching.calculate_match(student, opp)

        # Since all skills are matched with high proficiency, score should be >= 90%
        self.assertGreaterEqual(res['match_percentage'], 90.0)
        self.assertIn('Python', res['matched_skills'])
        self.assertIn('SQL', res['matched_skills'])
        self.assertEqual(len(res['missing_skills']), 0)

if __name__ == '__main__':
    unittest.main()
