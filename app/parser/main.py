from .banking.parser import BaseBankingParser
from .buyer.parser import AccountTicketsService
from .drivers import WebDriversService
from .loginer.parser import PlatformLoginParser
from .proxies.services import ProxiesService
from .replenisher.parser import AccountReplenishmentParser


class PlatformLeadsService:
    def __init__(self,
                 drivers_service: WebDriversService = WebDriversService()):
        self._drivers_service = drivers_service

    def mass_generate(self, ref_link: str, count: int, proxy: list[str]):
        ...
