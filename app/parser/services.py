import asyncio
import os

from .exceptions import CountLeadsOverflowError


class PlatformLeadsService:
    _MAX_LEADS_COUNT: int = os.environ.get("MAX_LEADS_PER_SESSION")

    def __init__(self, loginer: ...,
                 replenisher: ...,
                 buyer: ...,
                 max_leads_count: int = None):
        self._loginer = loginer
        self._replenisher = replenisher
        self._buyer = buyer
        self._MAX_LEADS_COUNT = max_leads_count or self._MAX_LEADS_COUNT

    async def mass_generate(self, count: int):
        if count > self._MAX_LEADS_COUNT:
            raise CountLeadsOverflowError

        mass_result = await asyncio.gather(
            *[_generate() for _ in range(0, count)]
        )

        return mass_result

    async def _generate(self):
        # await self._loginer.login(...)
        #
        # await self._replenisher.replenish()
        #
        # await self._buyer.buy_target()

        return True
