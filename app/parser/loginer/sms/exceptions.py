class SMSServiceError(BaseException):
    pass


class BadResponseGettingPhoneNumber(BaseException):
    pass


class SMSReceiveTimeout(BaseException):
    pass
