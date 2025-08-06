from abc import ABCMeta, abstractmethod


class BaseMailCredentialsFormatter(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, *args, raw_credentials: str, **kwargs):
        pass

    @abstractmethod
    def formated(self):
        pass
