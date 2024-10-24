class BadPhoneNumber(BaseException):
    pass


class ForceLogin(BaseException):
    pass


class LoginFailedAfterRetries(BaseException):
    pass


class AccountExists(BaseException):
    pass


class ErrorEnteringAccountData(BaseException):
    pass
