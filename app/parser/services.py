import asyncio
import copy
import os
import threading
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

    _results = copy.copy([])

    def __init__(self,
                 payments_service: BaseBankingParser = BaseBankingParser(),
                 loginer: PlatformLoginParser = PlatformLoginParser,
                 replenisher: AccountReplenishmentParser = AccountReplenishmentParser,
                 buyer: AccountTicketsService = AccountTicketsService,
                 drivers_service: WebDriversService = WebDriversService()):
        self._loginer = loginer
        self._replenisher = replenisher
        self._buyer = buyer
        self._drivers_service = drivers_service
        self._payments_service = payments_service

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(PlatformLeadsService, cls).__new__(cls)

        return cls.instance

    def mass_generate(self, ref_link: str, count: int, proxy: list[str]):
        if count > self._MAX_LEADS_COUNT:
            raise CountLeadsOverflowError

        leads = []

        for i in range(count):
            thread = threading.Thread(target=self.generate_no_async,
                                      args=(ref_link, proxy[i]))

            thread.start()

            leads.append(thread)

        [i.join(timeout=1200) for i in leads]

        return self._results

        # for gen_id in range(0, count):
        #     yield f"-> Start generation #{gen_id}"
        #     try:
        #         async for step_msg in self.generate(ref_link, proxy[gen_id]):
        #             if not step_msg:
        #                 yield f"# {gen_id} ✅ Successed"
        #             else:
        #                 yield f" - {step_msg}"
        #
        #     except Exception as e:
        #         yield f"#{gen_id} ❌ Error {repr(e)}"

    def generate_no_async(self, ref_link: str, proxy: str = None):
        asyncio.run(self.generate(ref_link, proxy))

    async def generate(self, ref_link: str, proxy: str = None):
        account_driver = await self._drivers_service.get(proxy=proxy)

        loginer: PlatformLoginParser = self._loginer(driver=account_driver)
        # replenisher: AccountReplenishmentParser = self._replenisher(driver=account_driver)

        # yield "✅Services Initialized"

        number = acc_data = None

        try:
            async for step in loginer.login(ref_link=ref_link):
                if type(step) == str:
                    pass
                else:
                    _, number, acc_data = step
                    break

            # yield "✅Logined"

            qr_path = self._buyer(driver=account_driver).get_qr()

            # yield "✅Balance replenished"

            self._payments_service.pay_qr(path=qr_path)
            self._results.append([True, acc_data, ""])

        except Exception as e:
            # yield "✅Success lead generated!"
            self._results.append([False, acc_data, e])
