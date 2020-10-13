import unittest
from pizzaweb import app, mongoclient


class BasicTests(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        self.app = app.test_client()
        self.assertEqual(app.debug, False)
        db = mongoclient['Pizza']
        db.Pizzas.drop()
        db.Codes.drop()
        db.Pizzas.insert_one({"name": "initaldbtest", 'pizzatype': "Pepperoni", "code": "12345"})
        db.Codes.insert_one({'code': '12345'})

    # executed after each test
    def tearDown(self):
        pass

    def test_main_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_admin_page(self):
        response = self.app.get('/admin', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_createcode_page(self):
        response = self.app.get('/newcode', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_error(self):
        response = self.app.get('/input?fname=thisistoolong123&dropdown=Pepperoni&code=12345', follow_redirects=True)
        self.assertEqual(response.status_code, 400)

    def test_confirmation_page(self):
        response = self.app.get('/confirmation', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_order(self):
        response = self.app.get('/input?fname=webtest&dropdown=Pepperoni&code=12345', follow_redirects=True)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
