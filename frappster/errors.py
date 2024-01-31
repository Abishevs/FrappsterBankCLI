class InvalidAmountError(Exception):
    def __str__(self):
        return "Invalid amount specified. Please enter a valid amount."

class InsufficientFundsError(Exception):
    def __str__(self):
        return "Insufficient funds in the account for this transaction."

class AccountNotFoundError(Exception):
    def __str__(self):
        return "The specified account could not be found. Please check the account details."

class GeneralError(Exception):
    def __str__(self):
        return "An unexpected error occurred. Please try again later."

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
    def __str__(self):
        return "A database error occurred. Please try again later."

class TooManyLoginAttemptsError(Exception):
    def __str__(self):
        return "Locked. Too many login attempts."

class LoginTimeoutError(Exception):
    def __str__(self):
        return "Login attempts locked. Please try again later."

class InvalidCommandError(Exception):
    def __str__(self):
        return "Invalid command"

