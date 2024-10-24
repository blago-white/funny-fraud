class CardNumberEnterRequired(BaseException):
    pass


class PasswordSetRequired(BaseException):
    pass


class PasswordEnterRequired(BaseException):
    pass


class AuthError(BaseException):
    pass


class ReEnterOtp(BaseException):
    pass
