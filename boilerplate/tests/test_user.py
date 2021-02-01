import unittest
import json

from boilerplate.services.users import user_service
from boilerplate.tests import BaseTestCase, User


class PasswordHashingTests(BaseTestCase):

    def test_password_setter(self):
        u = User(username="Test",
                 email="test@test.com",
                 password='cat')

        self.assertIsNotNone(u._password)

    def test_password_verification(self):
        u = User(username="Test",
                 email="test@test.com",
                 password='cat')

        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u1 = User(username="Test",
                  email="test@test.com",
                  password='cat')

        u2 = User(username="Test2",
                  email="test2@test.com",
                  password='cat')

        self.assertNotEqual(u1._password, u2._password)


class UserApiTests(BaseTestCase):

    def test_get_all_users(self):
        with self.client:
            user1 = user_service.create_user(username="Test1",
                                             email="Test1@Test.com",
                                             password="12345")

            user1_str = repr(user1)
            self.assertIn(user1.username, user1_str)
            self.assertIn(user1.email, user1_str)

            user2 = user_service.create_user(username="Test2",
                                             email="Test2@Test.com",
                                             password="12345")

            response = self.client.get("/api/1/users/all")
            self.assert200(response)

            content = json.loads(response.get_data(as_text=True))

            # Check json envelope
            self.assertIn('users', content.keys())

            # Check json fields
            self.assertIn('username', content['users'][0].keys())
            self.assertIn('email', content['users'][0].keys())
            self.assertIn('password', content['users'][0].keys())
            self.assertIn('image_file', content['users'][0].keys())

            # Check that the first user we got is
            # equal to the first user we created
            self.assertEqual(content['users'][1]['username'],
                             user1.username)
            self.assertEqual(content['users'][1]['email'],
                             user1.email)
            self.assertEqual(content['users'][1]['password'],
                             user1._password.decode("utf-8"))
            self.assertEqual(content['users'][1]['image_file'],
                             user1.image_file)

            # Check that the second user we got is
            # equal to the second user we created
            self.assertEqual(content['users'][2]['username'],
                             user2.username)
            self.assertEqual(content['users'][2]['email'],
                             user2.email)
            self.assertEqual(content['users'][2]['password'],
                             user2._password.decode("utf-8"))
            self.assertEqual(content['users'][2]['image_file'],
                             user2.image_file)

    def test_add_users(self):
        with self.client:
            # Check if we can successfully add user
            response = self.client.post("/api/1/users/add",
                                        data=dict(username="test",
                                                  email="test@test.com",
                                                  password="12345"))
            self.assert_status(response, 201)

            # Check if we can get user added from endpoint
            response_get = self.client.get("/api/1/users/all")
            self.assert200(response_get)

            content = json.loads(response_get.get_data(as_text=True))
            self.assertEqual(content['users'][1]['username'], 'test')
            self.assertEqual(content['users'][1]['email'], 'test@test.com')

            # Check if we can add user with invalid parameters
            response = self.client.post("/api/1/users/add",
                                        data=dict(username="1",
                                                  email="1",
                                                  password="1"))
            self.assert_status(response, 422)

            # Check if we can add user with missing parameters
            response = self.client.post("/api/1/users/add",
                                        data=dict(username="test",
                                                  email="test"))
            self.assert_status(response, 400)

    def test_get_user_by_id(self):
        with self.client:
            user = user_service.create_user(username="testing",
                                            email="testing@testing.com",
                                            password="12345")
            response = self.client.get("/api/1/users/2")
            self.assert200(response)

            # Check if the user we got is equal to the one created
            content = json.loads(response.get_data(as_text=True))

            self.assertIn('user', content.keys())
            self.assertEqual(content['user']['username'],
                             user.username)
            self.assertEqual(content['user']['email'],
                             user.email)
            self.assertEqual(content['user']['password'],
                             user._password.decode("utf-8"))
            self.assertEqual(content['user']['image_file'],
                             user.image_file)

            # Check if we can get a user that doesn't exist
            response = self.client.get("/api/1/users/6")
            self.assert404(response)


if __name__ == '__main__':
    unittest.main()  # pragma: no cover
