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

