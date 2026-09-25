import unittest
import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app

class TestFlaskEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_landing_page(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'EduConnect AI', res.data)
        self.assertIn(b'Smart Automation', res.data)

    def test_student_login_and_dashboard(self):
        # Demo role switch to student
        res = self.client.get('/switch-role/student', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Rahul Sharma', res.data)
        self.assertIn(b'AI Readiness Index', res.data)

    def test_assessment_submit_api(self):
        # Login as student first
        self.client.get('/switch-role/student')
        payload = {
            'answers': {
                '1': 'B',
                '2': 'B',
                '3': 'C',
                '4': 'A',
                '5': 'B'
            }
        }
        res = self.client.post('/api/assessment/submit', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertIn('overall_readiness', data['result'])

    def test_company_dashboard_and_applicants(self):
        self.client.get('/switch-role/company')
        res = self.client.get('/company/dashboard')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'TechCorp Innovations', res.data)

        # Check applicants
        res2 = self.client.get('/company/applicants')
        self.assertEqual(res2.status_code, 200)
        self.assertIn(b'Applicant Pool', res2.data)

    def test_college_dashboard_and_analytics_api(self):
        self.client.get('/switch-role/college')
        res = self.client.get('/college/dashboard')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'National Institute of Engineering', res.data)

        # Test analytics API
        res2 = self.client.get('/api/college/analytics')
        self.assertEqual(res2.status_code, 200)
        data = json.loads(res2.data)
        self.assertIn('total_students', data)
        self.assertIn('average_skill_score', data)

    def test_public_portfolio(self):
        res = self.client.get('/portfolio/rahul-sharma')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Rahul Sharma', res.data)
        self.assertIn(b'Verified Certifications', res.data)

if __name__ == '__main__':
    unittest.main()
