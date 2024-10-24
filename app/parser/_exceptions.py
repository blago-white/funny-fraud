class CountLeadsOverflowError(BaseException):
    msg = "Укажите кол-во заявок меньше"


class AccountReplenishmentError(BaseException):
    msg = "Невозможно пополнить аккаунт"
