from enum import Enum, auto

class AccountType(Enum):
    SAVINGS = 10
    CHECKINGS = 20
    BUSINESS = 30

class AccessRole(Enum):
    CUSTOMER = 1
    EMPLOYEE = 2
    ADMIN = 3

class Permissions(Enum):
    # User
    MANAGE_USERS = auto() # Global can do CRUD
    UPDATE_OWN_USER = auto()
    CREATE_USER = auto()
    VIEW_USER = auto()
    UPDATE_USER = auto()
    DELETE_USER = auto()

    # Accounts
    VIEW_ACCOUNT_DETAILS = auto()
    FREEZE_ACCOUNT = auto()
    MANAGE_ACCOUNTS = auto() # General
    CREATE_ACCOUNT = auto()
    VIEW_ACCOUNT = auto()
    DELETE_ACCOUNT = auto()
    UPDATE_ACCOUNT = auto()
    CLOSE_ACCOUNT = auto()

    # Transactions
    VIEW_ALL_TRANSACTIONS = auto()
    VIEW_USER_TRANSACTIONS = auto()
    VIEW_OWN_TRANSACTIONS = auto()
    INITIATE_TRANSACTION = auto()
    INITIATE_OWN_TRANSACTION = auto()
    MAKE_DEPOSIT = auto()
    MAKE_WITHDRAWL = auto()

    # logs
    VIEW_AUDIT_LOGS = auto()
    VIEW_ERROR_LOGS = auto()

ROLE_PERMISSIONS = {
    AccessRole.ADMIN: [Permissions.MANAGE_USERS,
                       Permissions.MANAGE_ACCOUNTS,
                       Permissions.FREEZE_ACCOUNT,
                       Permissions.VIEW_ALL_TRANSACTIONS,
                       Permissions.VIEW_AUDIT_LOGS,
                       Permissions.VIEW_ERROR_LOGS,
                       ],
    AccessRole.EMPLOYEE: [Permissions.MANAGE_USERS,
                          Permissions.MANAGE_ACCOUNTS,
                          Permissions.VIEW_ALL_TRANSACTIONS,
                          Permissions.INITIATE_TRANSACTION,
                          ],
    AccessRole.CUSTOMER: [Permissions.VIEW_OWN_TRANSACTIONS,
                          Permissions.INITIATE_OWN_TRANSACTION,
                          Permissions.UPDATE_OWN_USER,
                          ],
}
 


