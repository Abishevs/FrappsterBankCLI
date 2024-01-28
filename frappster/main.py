# from frappster.database import DatabaseManager
# from frappster.models import User
# from frappster.services import AuthService, UserManager
# from frappster.types import AccessRole
from frappster.ui.app import BankingApp

def main():
    app = BankingApp()
    app.run()
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
    # # print(new_user.id)
    # user = user_manager.get_user(2)
    # auth_service.current_user = user
    # auth_service.update_password(user, "alicee")
    # print(user.access_role)

if __name__ == "__main__":
    main()
