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

    async def info(self):
        session = aiohttp.ClientSession()

        return await self._request_authenticated(
            method="get",
            url="https://proxy.family/api/user/info",
            session=session
        )

    async def buy_proxy(self, count: int) -> list[str]:
        session = aiohttp.ClientSession()

        return await self._buy(count=count, session=session)

    async def _buy(
            self, count: int,
            session: aiohttp.ClientSession) -> list[str]:
        transaction_time = time.time()

        data = await self._request_authenticated(
            method="post",
            url=f"https://proxy.family/api/order/create"
                f"?tariff_id=1&term_days=1&count={count}"
                f"&proxy_login=admin&proxy_password={transaction_time}",
            session=session
        )

        if not data.get("successful"):
            raise ErrorBuyProxies(str(data))

        return self._get_by_transaction_time(
            time_=str(transaction_time),
            session=session
        )

    async def _get_by_transaction_time(
            self, time_: str,
            session: aiohttp.ClientSession
            ) -> list[str]:
        data = self._request_authenticated(
            method="get",
            url="https://proxy.family/api/proxy/list&sort=DESC",
            session=session
        )

        if not data.get("successful"):
            raise ErrorBuyProxies(data)

        return self._retrieve_relevant_proxy(
            time_=time_,
            response=data
        )

    def _retrieve_relevant_proxy(self, time_: str,
                                 response: dict) -> list[str]:
        proxies: dict[str, dict] = response.get(
            "data", {}
        ).get("proxies")

        proxies_serialized = []

        if proxies:
            for id_, data in proxies.items():
                if data.get("password") == time_:
                    proxies_serialized.append(
                        f"http://{data.get('login')}:{data.get('password')}@"
                        f"{data.get('ip')}:{data.get('http_port')}"
                    )

        return proxies_serialized

    async def _request_authenticated(
            self, method: str,
            url: str,
            session: aiohttp.ClientSession) -> dict:
        async with session.request(
                method=method,
                url=url,
                headers={
                    "Api-Token": self._APIKEY
                }
        ) as response:
            data = await response.json()

            if not response.ok:
                raise ErrorBuyProxies(data.get("error"))

            return data
