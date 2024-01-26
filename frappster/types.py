from enum import Enum, auto

class AccountType(Enum):
    SAVINGS = auto()
    CHECKING = auto()
    BUSINESS = auto()

class AccessRole(Enum):
    ADMIN = auto()
    EMPLOYEE = auto()
    CUSTOMER = auto()

class Permissions(Enum):
    # User
    MANAGE_USERS = auto()
    UPDATE_OWN_USER = auto()

    # Accounts
    VIEW_ACCOUNT_DETAILS = auto()
    FREEZE_ACCOUNT = auto()
    MANAGE_ACCOUNTS = auto()

    # Transactions
    VIEW_ALL_TRANSACTIONS = auto()
    VIEW_USER_TRANSACTIONS = auto()
    VIEW_OWN_TRANSACTIONS = auto()
    INITIATE_TRANSACTION = auto()
    INITIATE_OWN_TRANSACTION = auto()

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
    AccessRole.EMPLOYEE: [Permissions.MANAGE_ACCOUNTS,
                          Permissions.MANAGE_USERS,
                          Permissions.VIEW_ALL_TRANSACTIONS,
                          Permissions.INITIATE_TRANSACTION,
                          ],
    AccessRole.CUSTOMER: [Permissions.VIEW_OWN_TRANSACTIONS,
                          Permissions.INITIATE_OWN_TRANSACTION,
                          Permissions.UPDATE_OWN_USER,
                          ],
}
 


