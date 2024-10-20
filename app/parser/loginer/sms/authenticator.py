import os
import time

import aiohttp

from .exceptions import (BadResponseGettingPhoneNumber,
                         SMSReceiveTimeout,
                         SMSServiceError)


class SMSAuthenticator:
    _apikey: str
    __session: aiohttp.ClientSession = None

    _API_ROUTES = {
        "balance": "https://365sms.ru/stubs/handler_api.php?"
                   "api_key={api}&action=getBalance",
        "number": "https://365sms.ru/stubs/handler_api.php"
                  "?api_key={api}&action=getNumber"
                  "&service=wd&operator=mts&country=0",
        "set-status": "https://365sms.ru/stubs/handler_api.php?"
                      "api_key={api}&action=setStatus&status=8&id={id}",
        "get-code": "https://365sms.ru/stubs/handler_api.php?"
                    "api_key={api}&action=getStatus&id={id}"
    }

    def __init__(self, apikey: str = os.environ.get("SMS_SERVICE_APIKEY")):
        self._apikey = apikey or os.environ.get("SMS_SERVICE_APIKEY")

    @property
    async def _session(self) -> aiohttp.ClientSession:
        if not self.__session:
            self.__session = aiohttp.ClientSession()

        return self.__session

    async def get_balance(self) -> float:
        async with (await self._session).get(
            self._API_ROUTES.get("balance").format(api=self._apikey)
        ) as response:
            if not response.ok:
                await self.close()
                raise SMSServiceError("Error retrieve balance")

        data: str = response.text

        return float(data.split(":")[-1])

    async def cancel(self, activation_id: int):
        async with (await self._session).get(
            self._API_ROUTES.get("set-status").format(
                api=self._apikey,
                id=str(activation_id)
            )
        ) as response:
            if (not response.ok) or (await response.text() != "ACCESS_CANCEL"):
                await self.close()
                raise SMSServiceError("Error canceling number rent")

    async def get_status(self, activate_id: int) -> str | None:
        async with (await self._session).get(
            self._API_ROUTES.get("get-code").format(
                api=self._apikey,
                id=str(activate_id)
            )
        ) as response:
            if not response.ok:
                return None

            response = await response.text()

            if "STATUS_OK" in response:
                return response.split(":")[-1]

    async def get_number(self) -> list[int, int]:
        async with (await self._session).get(
            self._API_ROUTES.get("number").format(api=self._apikey)
        ) as response:
            if not response.ok:
                raise BadResponseGettingPhoneNumber(await response.text())

            response = await response.text()

        if not ("ACCESS_NUMBER" in response):
            await self.close()
            raise BadResponseGettingPhoneNumber(
                f"Not correct response: {response}"
            )

        return [int(i) for i in response.split(":")[1:]]

    async def close(self):
        await self.__session.close()
