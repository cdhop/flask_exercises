import unittest
from app import app

class BasicTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_user(self):
        response = self.app.get('/user/Chris')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Chris' in str(response.data))

    def test_response(self):
        response = self.app.get('/response')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('cookie' in str(response.data))

    def test_redirect(self):
        response = self.app.get('/redirect_example')
        self.assertEqual(response.status_code, 302)

if __name__ == '__main__':
    unittest.main()
