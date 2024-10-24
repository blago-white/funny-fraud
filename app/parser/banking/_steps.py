from abc import ABCMeta, abstractmethod


class BaseStep:
    @property
    @abstractmethod
    def CODE(self):
        pass


class EnterOtp(BaseStep):
    CODE = "ведите код"


class EnterPassword(BaseStep):
    CODE = "Введите пароль"


class EnterCardNumber(BaseStep):
    CODE = "Введите номер карты"


class CreatePin(BaseStep):
    CODE = "Придумайте код"


class CreatePassword(BaseStep):
    CODE = "Придумайте пароль"


class EnterPin(BaseStep):
    CODE = "Здравствуйте,"


STEPS = [EnterPassword, EnterCardNumber, CreatePin, CreatePassword, EnterPin]


def get_by_title(title: str) -> BaseStep | None:
    for s in STEPS:
        if s.CODE in title:
            return s

    return None
