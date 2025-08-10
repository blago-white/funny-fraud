from .profiles.drivers import WebDriversService
from .sessions import LeadsGenerationSession
from .parser.parser import StolotoTicketsParser
from .utils.sms.helpersms import HelperSMSService


class PlatformLeadsService:
    def __init__(self,
                 parser: StolotoTicketsParser = None,
                 sms_service: HelperSMSService = None,
                 drivers_service: WebDriversService = WebDriversService()):
        self._drivers_service = drivers_service
        self._sms_service = sms_service or HelperSMSService()
        self._parser = parser or StolotoTicketsParser

    def mass_generate(self, ref_link: str, count: int, proxy: list[str]):
        ...

    def generate(self, session: LeadsGenerationSession):
        for _ in range(5):
            pass

        self._parser.register_phone(phone=...)
