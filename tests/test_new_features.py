import unittest
import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app

class TestNewFeatures(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_company_search_api(self):
        res = self.client.get('/api/companies/search?q=tech')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertIn('TechCorp', data[0]['company_name'])

    def test_company_follow_toggle(self):
        # Login as student
        self.client.get('/switch-role/student')
        
        # Follow company with ID 1
        res = self.client.post('/api/company/1/follow')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertIn('following', data)

    def test_messaging_api(self):
        # Switch to student (Rahul Sharma, user_id=1)
        self.client.get('/switch-role/student')

        # Send a message to user_id=2 (TechCorp recruiter)
        payload = {
            'recipient_id': 2,
            'content': 'Hello from Rahul! Excited about the Cloud Developer opening.'
        }
        res = self.client.post('/api/messages/send', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertIn('message', data)

        # Retrieve conversation history
        res2 = self.client.get('/api/messages/history/2')
        self.assertEqual(res2.status_code, 200)
        t_data = json.loads(res2.data)
        self.assertIn('messages', t_data)
        self.assertGreater(len(t_data['messages']), 0)

        # Check unread count
        res3 = self.client.get('/api/messages/unread-count')
        self.assertEqual(res3.status_code, 200)
        u_data = json.loads(res3.data)
        self.assertIn('unread_count', u_data)

    def test_ai_advisor_chat_api(self):
        self.client.get('/switch-role/student')
        payload = {
            'message': 'How can I prepare for a Full Stack Python role?'
        }
        res = self.client.post('/api/ai/advisor/chat', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertIn('reply', data)
        self.assertGreater(len(data['reply']), 20)

    def test_ai_cover_letter_generator(self):
        self.client.get('/switch-role/student')
        payload = {
            'opportunity_title': 'Junior Python Backend Engineer',
            'company_name': 'TechCorp Innovations'
        }
        res = self.client.post('/api/ai/cover-letter', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertIn('cover_letter', data)
        self.assertIn('TechCorp Innovations', data['cover_letter'])

    def test_ai_extract_skills_from_resume(self):
        self.client.get('/switch-role/student')
        payload = {
            'text': 'Proficient in Python, Django, Docker, and PostgreSQL with experience deploying on AWS.'
        }
        res = self.client.post('/api/ai/extract-skills', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertIn('skills', data)
        self.assertIn('Python', data['skills'])

    def test_ai_learning_roadmap(self):
        self.client.get('/switch-role/student')
        payload = {
            'target_role': 'DevOps Engineer',
            'missing_skills': ['Docker', 'Kubernetes', 'CI/CD']
        }
        res = self.client.post('/api/ai/learning-roadmap', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertIn('roadmap', data)
        self.assertEqual(len(data['roadmap']), 4)

if __name__ == '__main__':
    unittest.main()
