import os
import time

import requests

from db.captcha import CaptchaServiceApikeyRepository

from .converters.base import BaseCaptchaScreenshotConverter
from .converters.b64 import CaptchaScreenB64Converter
from .data import CaptchaClickType
from .base import BaseCaptchaSolverAPIAdapter
from .translators.base import BaseInstructionsTranslator
from .translators.ru import RUInstructionsTranslator


class CapGuruApiAdapter(BaseCaptchaSolverAPIAdapter):
    _CAPGURU_INPUT_ENDPOINT = "http://api.cap.guru/in.php"
    _CAPGURU_OUTPUT_ENDPOINT = "http://api.cap.guru/res.php"
    _MAX_AWAITING_RETRIES = 3
    _AWAITING_TIME_SEC = 5

    _image_converter: BaseCaptchaScreenshotConverter

    def __init__(
            self, apikey: str = None,
            apikey_repository: CaptchaServiceApikeyRepository = CaptchaServiceApikeyRepository,
            image_converter: BaseCaptchaScreenshotConverter = CaptchaScreenB64Converter,
            instructions_translator: BaseInstructionsTranslator = RUInstructionsTranslator):
        self._apikey = apikey or apikey_repository().get_current()
        self._image_converter = image_converter
        self._translator = instructions_translator

    def solve_captcha(
            self,
            captcha_photo_path: str,
            text_instruction: str,
            click_type: CaptchaClickType = CaptchaClickType.RECAP2):
        order_id = self._send_captcha(
            captcha_photo_path=captcha_photo_path,
            text_instruction=text_instruction,
            click_type=click_type
        )

        for _ in range(self._MAX_AWAITING_RETRIES):
            time.sleep(self._AWAITING_TIME_SEC)

            if solve := self._try_get_solve(order_id=order_id):
                return solve

        raise TimeoutError("Cannot solve captcha!")

    def _try_get_solve(self, order_id: str):
        result_endpoint_url = self._CAPGURU_OUTPUT_ENDPOINT + '?key=' + self._apikey + '&id=' + order_id

        result = requests.get(url=result_endpoint_url).text

        if "OK" in result:
            return list(
                map(
                    int, result.replace("OK|", "").split(",")
                )
            )

    def _send_captcha(
            self,
            captcha_photo_path: str,
            text_instruction: str,
            click_type: CaptchaClickType) -> str:
        serialized_screenshot = self._image_converter(
            captcha_screenshot_path=captcha_photo_path
        ).serialized

        payload = dict(
            textinstructions=self._translator(text_instruction).translated,
            click=click_type.value,
            key=self._apikey,
            method=self._image_converter.result_datatype_name(),
            body=serialized_screenshot,
            json=1
        )

        response = requests.post(
            url=self._CAPGURU_INPUT_ENDPOINT,
            data=payload
        ).json()

        return response.get("request")

    @classmethod
    def _extract_coordinates(cls, response_string: str) -> list:
        cords_numbers_list = map(
            lambda cordspair: cordspair.split(","),
            response_string.replace(
                "y=", ""
            ).replace(
                "x=", ""
            ).split(":")[-1].split(";")
        )

        return list(map(
            lambda cordspair: (int(cordspair[0]), int(cordspair[1])),
            cords_numbers_list
        ))
