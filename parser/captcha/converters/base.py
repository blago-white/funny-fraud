from abc import ABCMeta, abstractmethod


class BaseCaptchaScreenshotConverter:
    def __init__(self, captcha_screenshot_path: str):
        self._screen_path = captcha_screenshot_path

    @classmethod
    @abstractmethod
    def result_datatype_name(cls):
        ...

    @abstractmethod
    def serialized(self):
        ...
