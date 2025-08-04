from base import BaseMailCredentialsFormatter


class HStockFormatter(BaseMailCredentialsFormatter):
    def __init__(self, credentials: str):
        self._raw_credentials = credentials.split("\n")

    @property
    def formated(self):
        jsoned_credentials = {}

        for credential in self._raw_credentials:
            credential = credential.split("\n")

            jsoned_credentials.update({
                "mail": credential[0].split(": ")[-1],
                "password": credential[2].split(": ")[-1],
                "number": credential[3].split(": ")[-1],
            })

        return jsoned_credentials
