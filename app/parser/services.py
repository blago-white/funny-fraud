import asyncio
import os
import time

from .banking.parser import BaseBankingParser
from .drivers import WebDriversService
from ._exceptions import CountLeadsOverflowError, AccountReplenishmentError
from .loginer.parser import PlatformLoginParser
from .replenisher.parser import AccountReplenishmentParser
from .buyer.parser import AccountTicketsService
from .proxies.services import ProxiesService


class PlatformLeadsService:
    _MAX_LEADS_COUNT: int = int(os.environ.get("MAX_LEADS_PER_SESSION") or 27)

    def __init__(self,
                 payments_service: BaseBankingParser = BaseBankingParser(),
                 loginer: PlatformLoginParser = PlatformLoginParser,
                 replenisher: AccountReplenishmentParser = AccountReplenishmentParser,
                 buyer: AccountTicketsService = AccountTicketsService,
                 drivers_service: WebDriversService = WebDriversService(),
                 proxy_service: ProxiesService = ProxiesService()):
        self._loginer = loginer
        self._replenisher = replenisher
        self._buyer = buyer
        self._drivers_service = drivers_service
        self._payments_service = payments_service
        self._proxy_service = proxy_service

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(PlatformLeadsService, cls).__new__(cls)

        return cls.instance

    async def mass_generate(self, ref_link: str, count: int):
        if count > self._MAX_LEADS_COUNT:
            raise CountLeadsOverflowError

        # proxies = await self._proxy_service.buy_proxy(
        #     count=count
        # )

        for gen_id in range(0, count):
            try:
                async for step_msg in self.generate(ref_link, ""):
                    if not step_msg:
                        yield f"# {gen_id} ✅ Successed"

            except Exception as e:
                yield f"#{gen_id} ❌ Error {e[:10]}"

        yield

    async def generate(self, ref_link: str, proxy: str = None):
        account_driver = await self._drivers_service.get(proxy=proxy)

        loginer: PlatformLoginParser = self._loginer(driver=account_driver)
        replenisher: AccountReplenishmentParser = self._replenisher(driver=account_driver)

        yield "✅Services Initialized"

        number = acc_data = None

        async for step in loginer.login(ref_link=ref_link):
            if type(step) == str:
                yield step
            else:
                _, number, acc_data = step
                break

        yield "✅Logined"

        qr_path = replenisher.get_payment_qr(account_phone=str(number))

        yield "✅Replenish QR retrieved"

        for _ in range(5):
            self._payments_service.pay_qr(path=qr_path)
            yield "✅Replenish balance"

            if replenisher.wait_for_balance():
                yield "✅Balance replenished"

                break
            else:
                raise AccountReplenishmentError(
                    f"Error replenishment of {number}:{acc_data}"
                )
        else:
            raise AccountReplenishmentError

        self._buyer(driver=account_driver).buy()

        yield "✅Success lead generated!"
        yield
