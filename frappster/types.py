from enum import Enum, auto

class AccountType(Enum):
    SAVINGS = auto()
    CHECKING = auto()
    BUSINESS = auto()

class AccessRole(Enum):
    ADMIN = auto()
    EMPLOYEE = auto()
    CUSTOMER = auto()
