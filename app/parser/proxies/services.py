import os
import time

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

            # raise NotEnoughtBalanceFunds

        return await self._buy(count=count, session=session)

    async def _check_count(self, count: int, session: aiohttp.ClientSession):
        async with session.get(
            url=f"https://proxy6.net/api/{api_key}/getcount?country=ru"
        ) as response:
            json = await response.json()

        return int(json["count"]) >= count

    async def _buy(self, count: int,
                   session: aiohttp.ClientSession) -> list[str]:
        transaction_time = time.time()

        async with session.get(
            url=f"https://proxy.family/api/order/create"
                f"?tariff_id=3&term_days=1&count={count}"
                f"&proxy_login=admin&proxy_password={transaction_time}"
        ) as response:
            json = await response.json()

        if not json.get("successful"):
            raise ErrorBuyProxies(str(json))

        return self._get_by_session_time(
            time_=transaction_time,
            session=session
        )

        # return [
        #     (f"http://{i.get('user')}:{i.get('pass')}@"
        #      f"{i.get('host')}:{i.get('port')}")
        #     for i in json.get("list")
        # ]

    async def _get_by_transaction_time(self, time_: float, session: aiohttp.ClientSession):
        async with session.get("https://proxy.family/api/proxy/list"
                               "&sort=DESC") as response:
            data: dict[str, str] = await response.json()

        if not data.get("successful"):
            raise ErrorBuyProxies(data)

    def _retrieve_relevant_proxy(self, time_: float, response: str):
        pass
