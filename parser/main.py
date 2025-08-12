import time
import typing

import selenium.common.exceptions

from db.mails.mails import MailCredsRepository
from db.number import DonationPhoneNumberRepository
from db.leads import LeadGenerationResultsService
from db.transfer import LeadGenResultStatus, AccountCredentials
from db.proxy import ProxyRepository

from .profiles.drivers import WebDriversService
from .sessions import LeadsGenerationSession
from .parser.parser import StolotoTicketsParser
from .utils.sms.helpersms import HelperSMSService
from .utils.sms import exceptions as sms_exceptions
from .parser import exceptions as parser_exceptions
from . import exceptions


class PlatformLeadsService:
    _NUMBER_REGISTRATION_ATTEMPTS = 5

    def __init__(self,
                 parser: StolotoTicketsParser = None,
                 leads_db: LeadGenerationResultsService = None,
                 sms_service: HelperSMSService = None,
                 proxy_service: ProxyRepository = None,
                 mails_repository: MailCredsRepository = None,
                 donations_phone_repository: DonationPhoneNumberRepository = None,
                 drivers_service: WebDriversService = WebDriversService()):
        self._drivers_service = drivers_service
        self._leads_db = leads_db or LeadGenerationResultsService()
        self._sms_service = sms_service or HelperSMSService()
        self._mails_repository = mails_repository or MailCredsRepository()
        self._parser = parser or StolotoTicketsParser
        self._proxy_service = proxy_service or ProxyRepository()

        donations_phone_repository = donations_phone_repository or DonationPhoneNumberRepository()
        self._donations_phone = donations_phone_repository.get_current()

    def mass_generate(self, ref_link: str, count: int, proxy: list[str]):
        ...

    def generate(self, session_id: int,
                 lead_id: int,
                 parser: StolotoTicketsParser,
                 session: LeadsGenerationSession):
        try:
            parser.open_registration_form(url=session.ref_link)
        except parser_exceptions.TraficBannedError as e:
            raise e
        except:
            raise parser_exceptions.TraficBannedError("Unknown error, maybe element not loaded on page!")

        change_status = self._get_method_for_changing_status(session_id, lead_id)

        change_status(LeadGenResultStatus.PHONE_CODE_PROGRESS)

        number = code = phone_already_registered =None

        for _ in range(self._NUMBER_REGISTRATION_ATTEMPTS):
            try:
                order_id, number = self._sms_service.get_number()
            except sms_exceptions.NumberGettingException as e:
                if _ == self._NUMBER_REGISTRATION_ATTEMPTS-1:
                    raise e
                continue

            if _ > 0:
                parser.drop_reg_form()
            for _ in range(3):
                try:
                    parser.register_phone(phone=number[1:])
                    break
                except parser_exceptions.PhoneAlreadyRegisteredError:
                    phone_already_registered = True
                    break
                except selenium.common.exceptions.ElementClickInterceptedException:
                    parser.drop_floctory_widget()
                    continue
                except TimeoutError:
                    raise exceptions.ProfileBannedError("Cannot enter otp code for registration!")

            if phone_already_registered:
                phone_already_registered = False
                continue

            try:
                code = self._get_sms_code(
                    lambda: parser.check_number_not_blocked(),
                    order_id=order_id
                )
            except TimeoutError:
                continue
            break

        if not (code and number):
            raise exceptions.ReloadLead("SMS Code or NUMBER variables empty!!!")

        try:
            parser.enter_reg_sms_code(code=code)
        except parser_exceptions.PageHeaderNotChangedError:
            raise parser_exceptions.NumberBlockedByStolotoError("Page header not changed, maybe blocked!")

        mail = self._mails_repository.next()

        change_status(LeadGenResultStatus.ACCOUNT_REG_PROGRESS)

        self._leads_db.change_status(
            session_id=session_id,
            lead_id=lead_id,
            credentials=AccountCredentials(
                mail_credentials=mail,
                number=number
            )
        )

        try:
            parser.continue_registration(mail=mail)
        except parser_exceptions.AccountRegistrationPageWarning as e:
            print(f"LEAD #{lead_id} WARNING : {str(e)} [{repr(e)}]")

        try:
            parser.fill_profile_data()

            change_status(LeadGenResultStatus.TICKET_PURCHASING)

            parser.buy_ticket(ticket_recipient_phone=self._donations_phone)
        except Exception as e:
            print(f"LEAD #{lead_id} ERROR AFTER REGISTRATION {str(e)} {repr(e)}")

            change_status(LeadGenResultStatus.FAILED)
            self._leads_db.change_status(
                session_id=session_id,
                lead_id=lead_id,
                status=LeadGenResultStatus.FAILED,
                error=f"ERROR AFTER REGISTRATION, CHECK THE ACCOUNT!!! {str(e)} {repr(e)}"
            )

            raise exceptions.ErrorAfterRegistration(f"ERROR AFTER REGISTRATION {str(e)} {repr(e)}")
        else:
            change_status(LeadGenResultStatus.SUCCES_NO_VERIFIED_MAIL)

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

    def _get_method_for_changing_status(self, session_id: int, lead_id: int) -> typing.Callable:
        return lambda status: self._leads_db.change_status(session_id=session_id, lead_id=lead_id, status=status)
