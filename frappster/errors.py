class InvalidAmountError(Exception):
     # om användaren försöker sätta in, ta ut eller överföra ett
     # ogiltigt belopp (ex. negativt tal)
    pass

class InsufficientFundsError(Exception):
    # om användaren försöker ta ut eller överföra mer pengar än vad som
    # finns på kontot.
    pass

class AccountNotFoundError(Exception):
    # om användaren försöker överföra pengar till ett konto som inte
    # finns.
    pass

class GeneralError(Exception):
    # för oväntade fel
    pass

class PermissionDeniedError(Exception):
    def __str__(self):
        return "You do not have the necessary permissions to perform this action."

class UserNotFoundError(Exception):
    def __str__(self):
        return "The specified user was not found in the database."

class InvalidPasswordError(Exception):
    def __str__(self):
        return "The provided password is invalid. Please try again."

class InvalidPasswordOrIDError(Exception):
    def __str__(self):
        return "The provided password or ID is invalid. Please try again."

class UserNotLoggedInError(Exception):
    def __str__(self):
        return "No user is currently logged in. Please log in to continue."

class DatabaseError(Exception):
    pass
