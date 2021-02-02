import unittest
import os
import PIL

from flask_login import current_user
from boilerplate.tests import BaseTestCase
from boilerplate.dao.users import user_dao
from werkzeug.datastructures import FileStorage


class RouteTests(BaseTestCase):
    def test_home(self):
        response = self.client.get('/home', content_type='html/text')
        self.assert200(response)
        self.assert_template_used('home.html')
        self.assert_context("title", "Home")

    def test_about(self):
        response = self.client.get('/about', content_type='html/text')
        self.assert200(response)
        self.assert_template_used('about.html')
        self.assert_context("title", "About")

    def test_login(self):
        # Test that the page loads when not logged in
        response = self.client.get('/login', content_type='html/text')
        self.assert200(response)
        self.assert_template_used('login.html')
        self.assert_context("title", "Log in")

        # Test that a logged-in user is redirected to home
        with self.client:
            response = self.client.post(
                '/login',
                data=dict(email="ad@min.com", password="admin"),
                follow_redirects=True
            )
            self.assert200(response)
            self.assertTrue(current_user.is_active)
            self.assertTrue(current_user.is_authenticated)

            response = self.client.get('/login', content_type='html/text')

            # Another way of checking that a redirect happened
            # HTTP Code 302 means a redirect happened
            self.assert_status(response, 302)
            self.assert_template_used('home.html')

    def test_register(self):
        # Test that the page loads when not logged in
        response = self.client.get('/register', content_type='html/text')
        self.assert200(response)
        self.assert_template_used('register.html')
        self.assert_context("title", "Register")

        # Test that a logged-in user is redirected to home
        with self.client:
            response = self.client.post(
                '/login',
                data=dict(email="ad@min.com", password="admin"),
                follow_redirects=True
            )
            self.assert200(response)
            self.assertTrue(current_user.is_active)
            self.assertTrue(current_user.is_authenticated)

            response = self.client.get('/register', content_type='html/text')

            self.assert_status(response, 302)
            self.assert_template_used('home.html')

    def test_account(self):
        # Test before logging in
        response = self.client.get(
            '/account', content_type='html/text', follow_redirects=True
        )
        self.assert200(response)
        self.assert_template_used('login.html')
        self.assert_context("title", "Log in")
        self.assertIn(b'Please log in to access this page.', response.data)

        # Test after logging in
        with self.client:
            response = self.client.post(
                '/login',
                data=dict(email="ad@min.com", password="admin"),
                follow_redirects=True
            )
            self.assert200(response)
            self.assertTrue(current_user.is_active)
            self.assertTrue(current_user.is_authenticated)

            response = self.client.get('/account', content_type='html/text')

            # Another way of checking that a redirect happened
            # HTTP Code 302 means a redirect happened
            self.assert_status(response, 200)
            self.assert_template_used('account.html')

    def test_logout(self):
        response = self.client.get(
            '/logout', content_type='html/text', follow_redirects=True
        )
        self.assert200(response)
        self.assert_template_used('home.html')
        self.assert_context("title", "Home")


class LoginTests(BaseTestCase):
    def test_incorrect_login_password_empty(self):
        with self.client:
            response = self.client.post(
                '/login',
                data=dict(email="valid@email.com", password=""),
                follow_redirects=True
            )
            self.assertIn(b'This field is required.', response.data)
            self.assertFalse(current_user.is_active)
            self.assertFalse(current_user.is_authenticated)

    def test_correct_login(self):
        with self.client:
            response = self.client.post(
                '/login',
                data=dict(email="ad@min.com", password="admin"),
                follow_redirects=True
            )
            self.assert200(response)
            self.assertTrue(current_user.is_active)
            self.assertTrue(current_user.is_authenticated)
            self.assert_template_used('home.html')

    def test_incorrect_login(self):
        with self.client:
            response = self.client.post(
                '/login',
                data=dict(email="wrong@gmail.com", password="wrong"),
                follow_redirects=True
            )
            self.assertIn(b'Login unsuccessful!', response.data)
            self.assertFalse(current_user.is_active)
            self.assertFalse(current_user.is_authenticated)

    def test_logout(self):
        with self.client:
            self.client.post(
                '/login',
                data=dict(email="ad@min.com", password="admin"),
                follow_redirects=True
            )
            response = self.client.get('/logout', follow_redirects=True)
            self.assert200(response)
            self.assertFalse(current_user.is_active)
            self.assertFalse(current_user.is_authenticated)


class RegisterationTests(BaseTestCase):
    def test_incorrect_register_username_empty(self):
        with self.client:
            response = self.client.post(
                '/register',
                data=dict(
                    username="", email="test@gmail.com", password="test",
                    confirm_password="test"
                )
            )
            self.assertIn(b'This field is required.', response.data)
            self.assertFalse(current_user.is_active)
            self.assertFalse(current_user.is_authenticated)

    def test_incorrect_register_password_empty(self):
        with self.client:
            response = self.client.post(
                '/register',
                data=dict(
                    username="test", email="test@gmail.com", password="",
                    confirm_password="test"
                )
            )
            self.assertIn(b'This field is required.', response.data)
            self.assertFalse(current_user.is_active)
            self.assertFalse(current_user.is_authenticated)

    def test_incorrect_register_confirm_empty(self):
        with self.client:
            response = self.client.post(
                '/register',
                data=dict(
                    username="test", email="test@gmail.com", password="test",
                    confirm_password=""
                )
            )
            self.assertIn(b'This field is required.', response.data)
            self.assertFalse(current_user.is_active)
            self.assertFalse(current_user.is_authenticated)

    def test_invalid_register_username(self):
        with self.client:
            response = self.client.post(
                '/register',
                data=dict(
                    username="t", email="test@gmail.com", password="test",
                    confirm_password="test"
                )
            )
            self.assertIn(
                b'Field must be between 2 and 15 characters long.',
                response.data
            )
            self.assertFalse(current_user.is_active)
            self.assertFalse(current_user.is_authenticated)

    def test_invalid_register_confirm(self):
        with self.client:
            response = self.client.post(
                '/register',
                data=dict(
                    username="test", email="test@gmail.com", password="test",
                    confirm_password="test2"
                )
            )
            self.assertIn(b'Field must be equal to password.', response.data)
            self.assertFalse(current_user.is_active)
            self.assertFalse(current_user.is_authenticated)

    def test_invalid_register_username_old(self):
        with self.client:
            response = self.client.post(
                '/register',
                data=dict(
                    username="admin", email="test@gmail.com", password="test",
                    confirm_password="test"
                )
            )
            self.assertIn(b'Username already exists!', response.data)
            self.assertFalse(current_user.is_active)
            self.assertFalse(current_user.is_authenticated)

    def test_invalid_register_email_old(self):
        with self.client:
            response = self.client.post(
                '/register',
                data=dict(
                    username="test", email="ad@min.com", password="test",
                    confirm_password="test"
                )
            )
            self.assertIn(b'Account with email already exists!', response.data)
            self.assertFalse(current_user.is_active)
            self.assertFalse(current_user.is_authenticated)

    def test_correct_login(self):
        with self.client:
            email = "test@gmail.com"
            password = "test"
            response = self.client.post(
                '/register',
                data=dict(
                    username="test", email=email, password=password,
                    confirm_password=password
                ),
                follow_redirects=True
            )
            self.assert200(response)
            self.assertIn(
                b'Account created! You can now log in.', response.data
            )
            self.assertFalse(current_user.is_active)
            self.assertFalse(current_user.is_authenticated)

            response = self.client.post(
                '/login',
                data=dict(email=email, password=password),
                follow_redirects=True
            )
            self.assert200(response)
            self.assertTrue(current_user.is_active)
            self.assertTrue(current_user.is_authenticated)
            self.assert_template_used('home.html')


class AccountTests(BaseTestCase):

    def test_account_update_username(self):
        with self.client:
            response = self.client.post(
                '/login',
                data=dict(email="ad@min.com", password="admin")
            )

            self.assertStatus(response, 302)
            self.assertTrue(current_user.is_active)
            self.assertTrue(current_user.is_authenticated)

            response = self.client.post(
                '/account',
                data=dict(username="admin2")
            )
            self.assertStatus(response, 302)
            self.assertRedirects(response, '/account')
            self.assertMessageFlashed("Your account has been successfully"
                                      " updated!", 'success')

            user = user_dao.get_by_id(1)
            self.assertEqual(user.username, "admin2")

    def test_account_update_email(self):
        with self.client:
            response = self.client.post(
                '/login',
                data=dict(email="ad@min.com", password="admin")
            )

            self.assertStatus(response, 302)
            self.assertTrue(current_user.is_active)
            self.assertTrue(current_user.is_authenticated)

            response = self.client.post(
                '/account',
                data=dict(username="admin", email='ad2@min.com')
            )
            self.assertStatus(response, 302)
            self.assertRedirects(response, '/account')
            self.assertMessageFlashed("Your account has been successfully"
                                      " updated!", 'success')

            user = user_dao.get_by_id(1)
            self.assertEqual(user.email, 'ad2@min.com')

    def test_account_update_image(self):
        with self.client:
            response = self.client.post(
                '/login',
                data=dict(email="ad@min.com", password="admin")
            )

            self.assertStatus(response, 302)
            self.assertTrue(current_user.is_active)
            self.assertTrue(current_user.is_authenticated)

            cwd = os.getcwd()
            path = os.path.join(cwd + "/boilerplate/static/profile_pictures/",
                                      "d5d2195b1e812421.jpg")

            image = FileStorage(
                stream=open(path, "rb"),
                filename="test.jpg",
                content_type="image/jpeg",
            )

            response = self.client.post(
                '/account',
                data=dict(username="admin", email='ad2@min.com', image=image),
                content_type='multipart/form-data'
            )
            self.assertStatus(response, 302)
            self.assertRedirects(response, '/account')
            self.assertMessageFlashed("Your account has been successfully"
                                      " updated!", 'success')

            '''
            original_image = PIL.Image.open(path)
            new_path = os.path.join(cwd + "/boilerplate/static/profile_"
                                          "pictures/", current_user.image_file)
            new_image = PIL.Image.open(new_path)

            self.assertIsNone(PIL.ImageChops.difference(original_image,
                                                        new_image).getbbox())
            '''

            new_path = os.path.join(cwd + "/boilerplate/static/profile_"
                                          "pictures/", current_user.image_file)
            os.remove(new_path)

    def test_account_update_image_empty(self):
        with self.client:
            response = self.client.post(
                '/login',
                data=dict(email="ad@min.com", password="admin")
            )

            self.assertStatus(response, 302)
            self.assertTrue(current_user.is_active)
            self.assertTrue(current_user.is_authenticated)

            response = self.client.post(
                '/account',
                data=dict(username="admin", email='ad2@min.com', image=None),
                content_type='multipart/form-data'
            )
            self.assertStatus(response, 302)
            self.assertRedirects(response, '/account')
            self.assertMessageFlashed("Your account has been successfully"
                                      " updated!", 'success')

            user = user_dao.get_by_id(1)
            self.assertEqual(user.image_file, 'default.jpg')


if __name__ == '__main__':
    unittest.main()  # pragma: no cover
