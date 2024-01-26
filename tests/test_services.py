import unittest

from frappster.database import DatabaseManager
from frappster.models import User
from frappster.services import AuthService, UserManager
from frappster.types import AccessRole

    # db_manager = DatabaseManager()
    # auth_service = AuthService(db_manager)
    # user_manager = UserManager(db_manager)
    # user_manager = UserManager(db_manager)
    # new_user = user_manager.create_user(
    #         first_name="Alice",
    #         last_name="Smith",
    #         address="456 Elm Street",
    #         email="alice.smith@example.com",
    #         phone_number="987-654-3210",
    #         username="alicesmith",
    #         password="alicepassword",  
    #         access_role=AccessRole.ADMIN
    #         )
    #
    # user_manager.create_user(
    #         first_name="Alice",
    #         last_name="Smith",
    #         address="456 Elm Street",
    #         email="alice.smith@example.com",
    #         phone_number="987-654-3210",
    #         username="alicesmith",
    #         password="alicepassword",  
    #         access_role=AccessRole.CUSTOMER
    #         )
    # print(new_user.id)
    # user = user_manager.get_user(2)
    # auth_service.current_user = user
    # auth_service.update_password(user, "alicee")
    # print(user.access_role)

class TestUserManager(unittest.TestCase):

    def setUp(self):
        self.db_manager = DatabaseManager()
        self.user_manager = UserManager(self.db_manager)

    def test_create_user(self):

        user_id = self.user_manager.create_user(
            first_name="Alice",
            last_name="Smith",
            address="456 Elm Street",
            email="alice.smith@example.com",
            phone_number="987-654-3210",
            username="alicesmith",
            password="alicepassword",  
            access_role=AccessRole.ADMIN
        )
        self.assertEqual(user_id, 1)

    def test_get_user(self):

        user = self.user_manager.get_user(user_id=1)
        self.assertIsNotNone(user)
        self.assertEqual(user.id, 1)

if __name__ == '__main__':
    unittest.main()

