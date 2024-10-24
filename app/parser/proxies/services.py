import os

import aiohttp

from .exceptions import NotEnoughtBalanceFunds, ErrorBuyProxies


class ProxiesService:
    _APIKEY: str

    def __init__(self, apikey: str = None):
        if not apikey:
            self._APIKEY = os.environ.get("PROXY_SERVICE_APIKEY")
        else:
            self._APIKEY = apikey

    async def buy_proxy(self, count: int) -> list[str]:
        session = await aiohttp.ClientSession()

        if not await self._check_count(count=count, session=session):
            raise NotEnoughtBalanceFunds

        return await self._buy(count=count, session=session)

    async def _check_count(self, count: int, session: aiohttp.ClientSession):
        async with session.get(
            url=f"https://proxy6.net/api/{api_key}/getcount?country=ru"
        ) as response:
            json = await response.json()

        return int(json["count"]) >= count

    async def _buy(self, count: int,
                   session: aiohttp.ClientSession) -> list[str]:
        async with session.get(
            url=f"https://proxy6.net/api/"
                f"{self._APIKEY}/buy?count={count}&period=1&country=ru&nokey"
        ) as response:
            json = await response.json()

        if not json.get("status") == "yes":
            raise ErrorBuyProxies(str(json))

        return [
            (f"http://{i.get('user')}:{i.get('pass')}@"
             f"{i.get('host')}:{i.get('port')}")
            for i in json.get("list")
        ]
