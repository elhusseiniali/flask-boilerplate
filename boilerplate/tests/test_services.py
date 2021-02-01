import unittest
import pytest

from boilerplate.services.users import UserService, user_service
from boilerplate.dao.users import UserDAO
from boilerplate.tests import BaseTestCase, db, User


class UserServiceTests(BaseTestCase):

    @pytest.mark.xfail(raises=Exception)
    def test_singelton_service(self):
        UserService()

    @pytest.mark.xfail(raises=Exception)
    def test_singelton_DAO(self):
        UserDAO()

    def test_create_user(self):
        with self.client:
            user = user_service.create_user(username="Test",
                                            email="Test@Test.com",
                                            password="12345")

            user_db = db.session.query(User).get(user.id)

            self.assertEqual(user.username, user_db.username)

            user2 = user_service.create_user(username=None,
                                             email=None,
                                             password=None)

            self.assertIsNone(user2)

            user3 = user_service.create_user(username="Test",
                                             email="Test@Test.com",
                                             password="12345")

            self.assertIsNone(user3)

    def test_update_user(self):
        with self.client:
            user = user_service.create_user(username="Test",
                                            email="Test@Test.com",
                                            password="12345")

            user_db = db.session.query(User).get(user.id)

            no_id = user_service.update_user(user_id=None)
            self.assertFalse(no_id)

            no_params = user_service.update_user(user_id=user.id)
            self.assertFalse(no_params)

            username_updated = user_service.update_user(user_id=user.id,
                                                        username="Update")
            self.assertTrue(username_updated)
            self.assertEqual(user_db.username, "Update")
            self.assertEqual(user.username, user_db.username)

            email_updated = user_service.update_user(user_id=user.id,
                                                     email="Update@test.com")
            self.assertTrue(email_updated)
            self.assertEqual(user_db.email, "Update@test.com")
            self.assertEqual(user.email, user_db.email)

            image_file_updated = user_service.update_user(user_id=user.id,
                                                          image_file="Update."
                                                          "jpg")
            self.assertTrue(image_file_updated)
            self.assertEqual(user_db.image_file, "Update.jpg")
            self.assertEqual(user.image_file, user_db.image_file)

            updated = user_service.update_user(user_id=user.id,
                                               username="Update2",
                                               email="Update2@test.com",
                                               image_file="Update2.jpg")
            self.assertTrue(updated)
            self.assertEqual(user_db.username, "Update2")
            self.assertEqual(user_db.email, "Update2@test.com")
            self.assertEqual(user_db.image_file, "Update2.jpg")
            self.assertEqual(user.username, user_db.username)
            self.assertEqual(user.email, user_db.email)
            self.assertEqual(user.image_file, user_db.image_file)

            wrong_id = user_service.update_user(user_id=9,
                                                username="Update2",
                                                email="Update2@test.com",
                                                image_file="Update2.jpg")
            self.assertFalse(wrong_id)

            wrong_id_type = user_service.update_user(user_id="Test",
                                                     username="Update2",
                                                     email="Update2@test.com",
                                                     image_file="Update2.jpg")
            self.assertFalse(wrong_id_type)

    def test_delete_user(self):
        with self.client:
            user = user_service.create_user(username="Test",
                                            email="Test@Test.com",
                                            password="12345")

            no_id = user_service.delete_user(user_id=None)
            self.assertFalse(no_id)

            correct_id = user_service.delete_user(user_id=user.id)
            self.assertTrue(correct_id)

            bad_id = user_service.delete_user(user_id='NotAnInteger')
            self.assertFalse(bad_id)

            big_id = user_service.delete_user(user_id=100)
            self.assertFalse(big_id)


if __name__ == '__main__':
    unittest.main()  # pragma: no cover
