import base64

from .base import BaseCaptchaScreenshotConverter


class CaptchaScreenB64Converter(BaseCaptchaScreenshotConverter):
    @classmethod
    def result_datatype_name(cls):
        return "base64"

    @property
    def serialized(self):
        with open(self._screen_path, "rb") as file:
            return base64.b64encode(file.read())
