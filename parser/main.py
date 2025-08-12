import time

from db.mails.mails import MailCredsRepository
from db.number import DonationPhoneNumberRepository

from .profiles.drivers import WebDriversService
from .sessions import LeadsGenerationSession
from .parser.parser import StolotoTicketsParser
from .utils.sms.helpersms import HelperSMSService
from .parser import exceptions as parser_exceptions
from . import exceptions


class PlatformLeadsService:
    def __init__(self,
                 parser: StolotoTicketsParser = None,
                 sms_service: HelperSMSService = None,
                 mails_repository: MailCredsRepository = None,
                 donations_phone_repository: DonationPhoneNumberRepository = None,
                 drivers_service: WebDriversService = WebDriversService()):
        self._drivers_service = drivers_service
        self._sms_service = sms_service or HelperSMSService()
        self._mails_repository = mails_repository or MailCredsRepository()
        self._parser = parser or StolotoTicketsParser

        donations_phone_repository = donations_phone_repository or DonationPhoneNumberRepository()
        self._donations_phone = donations_phone_repository.get_current()

    def mass_generate(self, ref_link: str, count: int, proxy: list[str]):
        ...

    def generate(self, parser: StolotoTicketsParser, session: LeadsGenerationSession):
        parser.open_registration_form(url=session.ref_link)

        for _ in range(3):
            order_id, number = self._sms_service.get_number()

            if _ > 0:
                parser.drop_reg_form()

            try:
                parser.register_phone(phone=number[1:])
            except parser_exceptions.PhoneAlreadyRegisteredError:
                continue

            try:
                code = self._get_sms_code(
                    lambda: parser.check_number_not_blocked(),
                    order_id=order_id
                )
            except TimeoutError:
                continue
            break
        else:
            raise exceptions.ProfileBannedError()

        parser.enter_reg_sms_code(code=code)

        mail = self._mails_repository.next()

        parser.continue_registration(mail=mail)

        parser.fill_profile_data()

        payment_qr_path = parser.buy_ticket(
            ticket_recipient_phone=self._donations_phone
        )

    def _get_sms_code(self, *checks_functions, order_id: int, timeout: int = 200) -> str:
        START_WAITING = time.time()

        delta = lambda: time.time() - START_WAITING

        while (delta() < timeout) or not all([c() for c in checks_functions]):
            if type(code := self._sms_service.check_code(phone_id=order_id)) in (str, int):
                print(f"CODE RECEIVED: {code}")

                return code

            print("NO CODE")

            time.sleep(1)

        raise TimeoutError
