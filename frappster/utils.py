import bcrypt
import random
import decimal
from decimal import Decimal
from datetime import datetime, timedelta

from frappster.errors import InsufficientFundsError, InvalidAmountError, PermissionDeniedError

def is_valid_amount(amount, available_funds: Decimal | None = None):
    try:
        amount = Decimal(str(amount))
    except decimal.InvalidOperation:
        raise InvalidAmountError

    if amount < 0:
        raise InvalidAmountError 

    if amount == 0:
        raise InvalidAmountError

    if available_funds is not None:
        if amount > available_funds:
            raise InsufficientFundsError
    return amount

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'),
                                    salt)
    return hashed_password.decode('utf-8')

def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'),
                          hashed_password.encode('utf-8'))

def is_too_many_login_attempts(login_attempts: int, max_attempts: int = 3):
    return login_attempts > max_attempts

def reset_login_attempts(last_attempt: datetime, max_time_seconds: int = 30):
    time_diff = datetime.now() - last_attempt
    return time_diff >= timedelta(seconds=max_time_seconds)

def requires_role(minimum_role):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            if not hasattr(self, 'auth_service') or self.auth_service is None:
                raise AttributeError("AuthService instance is required for role check")

            current_user_role = self.auth_service.current_user.access_role
            if current_user_role.value < minimum_role.value:
                raise PermissionDeniedError
            return func(self, *args, **kwargs)
        return wrapper
    return decorator

def requires_permissions(*required_permissions):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            if not hasattr(self, 'auth_service') or self.auth_service is None:
                raise AttributeError("AuthService instance is required for permissions check")

            permissions_to_check = required_permissions
            # Unpack permissions if passed as a single list in args
            if len(args) > 0 and isinstance(args[0], list):
                permissions_to_check = args[0]
                args = args[1:]

            has_permision = False
            # If has atleast one given permsion, proceeeed
            for permission in permissions_to_check:
                if self.auth_service.has_permission(permission):
                    has_permision = True

            # if has none welp bye bye
            if not has_permision:
                raise PermissionDeniedError

            return func(self, *args, **kwargs)
        return wrapper
    return decorator

def gen_randomrange(digits=6):
    return random.randrange(111111, 999999, digits)


