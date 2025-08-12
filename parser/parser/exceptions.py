class TraficBannedError(Exception):
    pass


class RegOtpEnteringError(Exception):
    pass


class AccountRegistrationPageError(Exception):
    pass


class AccountRegistrationPageWarning(RuntimeWarning):
    pass


class NumberBlockedByStolotoError(Exception):
    pass


class PhoneAlreadyRegisteredError(Exception):
    pass


class UnsolvableCaptchaError(Exception):
    pass


class PageHeaderNotChangedError(Exception):
    pass
