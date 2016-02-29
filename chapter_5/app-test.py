import unittest
from hello import app

class BasicTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.asertTrue('success' in str(response.data))

if __name__ == '__main__':
    unittest.main()

