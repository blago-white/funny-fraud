import json
from json import JSONEncoder
from pathlib import Path

from .base import SimpleConcurrentRepository
from .exceptions import MailCredentialsValidationError, MailCredentialsEndedError
from .transfer import AccountMailCredentials

from .formatters.base import BaseMailCredentialsFormatter
from .formatters.hstock1 import HStockFormatter


lock = SimpleConcurrentRepository.locked


class MailCredsRepository(SimpleConcurrentRepository):
    _current: AccountMailCredentials = None
    _default_formatter: BaseMailCredentialsFormatter = HStockFormatter

    _STORAGE_FILE_PATH: str = Path(__file__).parent.parent / "data\\mails.json"

    @property
    @lock()
    def credentials_exists(self) -> tuple[bool, AccountMailCredentials | None]:
        credentials = self._current

        try:
            credentials.is_valid()
        except MailCredentialsValidationError:
            return False, credentials

        return True, None

    @lock()
    def next(self) -> str:
        if not self._current:
            raise MailCredentialsEndedError("Credentials storage is empty!")

        new_current_credentials = self._update_current_credential()

        print(f"RETRIEVE NEXT MAIL CREDENTIALS: {new_current_credentials}")

        return proxy

    @SimpleConcurrentRepository.locked()
    def add(self, data_set: str):
        formatted = self._default_formatter(credentials=data_set).formated

        last_credential = self._save_new_credentials(credentials=formatted)

        return last_credential

    def _update_current_credential(self):
        self._current = self._drop_last_credential()

        if self._current is None:
            raise MailCredentialsEndedError("Mail credentials was ended!")

        return self._current

    def _drop_last_credential(self):
        with open(self._STORAGE_FILE_PATH) as file:
            credentials = json.load(file)

        if not credentials:
            return

        new_current_credentials = credentials[1]

        with open(self._STORAGE_FILE_PATH, "w") as file:
            json.dump(credentials[1:], file)

        return new_current_credentials

    def _save_new_credentials(self, credentials: dict):
        with open(self._STORAGE_FILE_PATH, "w") as file:
            json.dump(credentials, file)

        with open(self._STORAGE_FILE_PATH) as file:
            credentials = json.load(file)

        return credentials[0]
