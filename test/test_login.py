import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

class TestLoginFunction(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_login_success(self):
        payload = {
            'username': 'admin@gmail.com',
            'password': 'password123'
        }
        response = self.client.post('/login.html', data=payload, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'admin@gmail.com', response.data) 

    def test_login_wrong_password(self):
        payload = {'username': 'admin@gmail.com', 'password': 'wrongpassword'}
        response = self.client.post('/login.html', data=payload, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid email or password', response.data)

    def test_login_empty_fields(self):
        payload = {'username': '', 'password': ''}
        response = self.client.post('/login.html', data=payload, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid email or password', response.data)

class TestLoginSession(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_logout_clears_session(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess['username'] = 'admin@gmail.com'
            res = c.get('/logout', follow_redirects=True)
            self.assertIn(b'You have been logged out.', res.data)

if __name__ == '__main__':
    unittest.main()
